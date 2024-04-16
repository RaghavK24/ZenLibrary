import os
from flask import request, jsonify,abort, make_response, send_file
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint
import json
from sqlalchemy import desc, func, or_, and_
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from celery.result import AsyncResult

from application.celery_worker import celery
from application.models import User,Book, Section, Order
from application.jwt import access
from application.db import db
from application.cache import cache
from application import tasks

routes = Blueprint("controller", __name__)

@routes.route("/login", methods=["POST"])
def login():
    '''Login route'''
    print("In the login method")
    data = request.get_json()
    print(data)
    username, password = data.get("username"), data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user:
        return make_response('user not found', 404)
    if not check_password_hash(user.password, password):
        return make_response('invalid password', 400)

    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    if not access_token or  not refresh_token:
        return make_response("error generating Token", 500)
    else:
        return jsonify(user=user.to_dict(), access_token=access_token)

@routes.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    return "logged out",200

@routes.route("/home", methods=["GET"])
@cache.memoize(timeout=50)
def home():
    '''home route'''
    try:
        sections = Section.query.filter(Section.approved==True).all()
        books = Book.query.all()
        # books = []
    except:
        return make_response(jsonify("error getting books"), 500)

    data = jsonify([section.to_dict() for section in sections], [book.to_dict() for book in books])
    return make_response(data, 200)

@routes.route("/admin", methods=["GET"])
@jwt_required()
@access(["admin"])
@cache.memoize(timeout=50)
def admin():
    data = {}
    data["users"] = User.query.count()
    data["section"] = Section.query.count()
    data["books"] = Book.query.count()
    data["orders_total"] = Order.query.count()
    data["managers"] = User.query.filter_by(role='manager').count()
    data["users"] = User.query.filter_by(role='user').count()
    data["revenue_total"] = Order.query.filter().with_entities(func.sum(Order.total_amount)).scalar()

    # data["orders_today"] = Order.query.filter(func.date(Order.created_timestamp) == datetime.today().date()).count()

    # orders from past 7 days
    orders_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        count = Order.query.filter(func.date(Order.created_timestamp) == date.date()).count()
        orders_data.append({"date":date.date().strftime('%d/%b'), "count": count})
    data["orders"] = orders_data

    # category wise products
    section_data = []
    sections = Section.query.all()
    for section in sections:
        section_dict = section.to_dict()
        section_data.append({'name':section_dict['name'], 'count': len(section.books)})
        # category_data.append(([category.to_dict(), len(category.products)]))
    data["sections"] = section_data

    #Revenue from past 7 days
    revenue_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        revenue = Order.query.filter(func.date(Order.created_timestamp) == date.date()).with_entities(func.sum(Order.total_amount)).scalar()
        if revenue is None:
            revenue = 0
        revenue_data.append({"date":date.date().strftime('%d/%b'), "total":revenue})
    data["revenue"] = revenue_data

    return jsonify(data), 200


@routes.route("/manager", methods=["GET"])
@jwt_required()
@access(["manager"])
@cache.memoize(timeout=50)
def manager():
    data = {}
    data["section"] = Section.query.count()
    data["books"] = Book.query.count()
    # data["revenue_today"] = 0
    data["revenue_today"] = Order.query.filter(func.date(Order.created_timestamp) == datetime.today().date()).with_entities(func.sum(Order.total_amount)).scalar()
    data["orders_today"] = Order.query.filter(func.date(Order.created_timestamp) == datetime.today().date()).count()

    # orders from past 7 days
    orders_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        count = Order.query.filter(func.date(Order.created_timestamp) == date.date()).count()
        orders_data.append({"date":date.date().strftime('%d/%b'), "count": count})
    data["orders"] = orders_data

    # category wise products
    section_data = []
    sections = Section.query.all()
    for section in sections:
        section_dict = section.to_dict()
        section_data.append({'name':section_dict['name'], 'count': len(section.books)})
        # category_data.append(([category.to_dict(), len(category.products)]))
    data["sections"] = section_data

    #Revenue from past 7 days
    revenue_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        revenue = Order.query.filter(func.date(Order.created_timestamp) == date.date()).with_entities(func.sum(Order.total_amount)).scalar()
        if revenue is None:
            revenue = 0
        revenue_data.append({"date":date.date().strftime('%d/%b'), "total":revenue})
    data["revenue"] = revenue_data

    return jsonify(data), 200


@routes.route("/sendreport", methods=["POST"])
@jwt_required()
@access(["manager"])
def send_report():
    print("In the generatecsv method")
    username = request.json.get('username')
    # print('username:', username)
    user = User.query.filter_by(username=username).first()
    if not user:
        return "user not found",404
    if user.role != "manager":
        return "user not authorized",403

    task = tasks.send_csv_report.delay(username)
    return jsonify({"taskid": task.id}), 200

@routes.route("/download-csv/<taskid>", methods=["GET"])
@jwt_required()
@access(["manager"])
def send_csv_report(taskid):
    pass
    result = celery.AsyncResult(taskid)
    if result.ready():
        file = result.result
        return send_file(file, as_attachment=True)
    else:
        return jsonify({"message":"task is pending"}), 200

@routes.route("/search", methods=["GET"])
@jwt_required()
@access(["user"])
def search():
    '''search products'''
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != "user":
        return make_response(jsonify("unauthorized"), 403)
    else:
        query = request.args.get('query')
        if query is None:
            return make_response(jsonify("empty search"), 400)

        sections = Section.query.filter(
            and_(Section.approved == True , Section.name.ilike("%" + query + "%"))
            ).all()

        section_books = []
        print(sections)
        for section in sections:
            section_books.extend([book for book in section.books])
            print(section_books)
            # category_products.extend(filter( lambda x: x.expiry_date >= datetime.now(), categories.products))

        books = Book.query.filter(
            or_(Book.name.ilike("%" + query + "%") ,
            Book.author.ilike("%" + query + "%") ,
            Book.price.ilike("%" + query + "%"))
            ).all()

        data = jsonify([section_book.to_dict() for section_book in section_books],
                       [book.to_dict() for book in books])
        return make_response(data, 200)

# from application.tasks import send_daily_reminder
# @routes.route("/dummy")
# def dummy():
#     tasks.send_daily_reminder.delay()
#     return "monthly report sent", 200
