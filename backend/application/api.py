from datetime import datetime
from zoneinfo import ZoneInfo
import os
import base64
import secrets
from io import BytesIO
import json

from PIL import Image
from flask import Blueprint, make_response, abort, Response, jsonify
from flask_restful import NotFound, Resource, fields, marshal_with, reqparse, request, inputs
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

from .db import db
from .config import UPLOAD_FOLDER
from .models import User, Section, Product, Item, Order
from .jwt import access
from flask import current_app as app
from .cache import cache

api = Blueprint("api", __name__)

class BadRequest(HTTPException):
    def __init__(self, message):
        self.response = make_response(message, 400)
class AlreadyExists(HTTPException):
    def __init__(self, message):
        self.response = make_response(message, 409)

class AuthenticationError(HTTPException):
    def __init__(self, message):
        self.response = make_response(message, 401)
class AuthorizationError(HTTPException):
    def __init__(self, message):
        self.response = make_response(message, 403)

class NotFound(HTTPException):
    def __init__(self, message):
        # self.response = make_response(message, 404)
        self.response = make_response(jsonify(message), 404)


class InternalError(HTTPException):
    def __init__(self, message):
        self.response = make_response(message, 500)


user_request_parse = reqparse.RequestParser(bundle_errors=True)
user_request_parse.add_argument("name", type=str, required=True)
user_request_parse.add_argument("username", type=str, required=True)
user_request_parse.add_argument("email", type=str, required=True)
user_request_parse.add_argument("approved", type=inputs.boolean)
user_request_parse.add_argument("role", type=str)
user_request_parse.add_argument("password", type=str)
user_request_parse.add_argument("image_name", type=str)
user_request_parse.add_argument("image", type=str)

class UserAPI(Resource):
    """
    User Object for managing users
    """
    @jwt_required()
    @cache.cached(timeout=50)
    def get(self, username=None):
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                data = jsonify(user.to_dict())
                return make_response(data, 200)
            else:
                raise NotFound("User not found")
        else:
            users = User.query.all()
            data = [user.to_dict() for user in users]
            return make_response(data, 200)

    def post(self):
        '''Create a new user'''
        args = user_request_parse.parse_args(strict=True)
        # print(args)
        name = args.get("name", None)
        username = args.get("username", None)
        email = args.get("email", None)
        role = args.get("role", None)
        password = args.get("password", None)
        image_name = args.get("image_name", None)
        image = args.get("image", None)

        # if args is None or name is None or username is None or password is None:
        if name is None or name == '':
            raise BadRequest("name not provided")
        if username is None or username == '':
            raise BadRequest("username not provided")
        if email is None or email == '':
            raise BadRequest("email not provided")
        if role is None or role == '':
            raise BadRequest("role not provided")
        else:
            if role == 'admin':
                raise AuthorizationError("admin role can not be created")
        if password is None or password == '':
            raise BadRequest("password not provided")
        # if len(password) < 4:
        #     raise BadRequest("password length is less than 4 chars")
        if image_name is None:
            image_name = 'default.png'
        else:
            image_name = secrets.token_hex(4) + '.png'

        # check if the user already exists based on username
        user = User.query.filter_by(username=username).first()
        if user is not None:
            print("=== user already exists === ")
            # raise BadRequest("user already exists")
            abort(Response("username already exists", 400))

        user = User.query.filter_by(email=email).first()
        if user is not None:
            print("==== email already registered ====")
            abort(Response("email already registered", 400))

        isapproved=True
        if role == 'manager':
            isapproved=False

        user = User(
            name=name,
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role,
            approved=isapproved,
            image_name=image_name,
            created_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
            updated_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
        )
        if user is None:
            raise InternalError(message="error in creating User")

        db.session.add(user)
        db.session.flush()

        # image = args.get("image", None)
        if image is not None and image_name is not None:
            try:
                if image_name == '':
                    raise BadRequest('image_name is empty')

                user.image_name = image_name

                file_data = base64.b64decode(image)
                basedir = os.path.abspath(os.path.dirname(__file__))
                filename= UPLOAD_FOLDER + '/images/users/' + image_name
                # print('Image filename to be saved: ', filename)

                # with open(filename, 'wb') as f:
                #     f.write(file_data)

                img = Image.open(BytesIO(file_data))
                img.resize((200, 200))
                img.save(filename, format='PNG')

            except:
                raise InternalError(message="error in saving image")
        else:
            image_name = 'default.png'
            user.image_name = image_name

        try:
            db.session.add(user)
            cache.clear()
            db.session.commit()
            cache.clear()
        except:
            raise InternalError(message="error in creating user")

        data = jsonify(user.to_dict())
        return make_response(data, 201)

    @jwt_required()
    def put(self, username=None):
        if username is None:
            raise BadRequest("username not given")
        else:
            args = user_request_parse.parse_args(strict=True)
            # print(args)

            user = User.query.filter_by(username=username).first()
            if user is not None:
                if user.username == "admin":
                    raise AuthorizationError(message="admin profile can not modified")
            else:
                raise NotFound(message="user not found")

            name = args.get("name", None)
            password = args.get("password", None)
            email = args.get("email", None)
            approved = args.get("approved", None)
            image = args.get("image",None)
            image_name = args.get("image_name", None)

            if email is None:
                email = user.email

            if image_name is None:
                image_name = user.image_name

            if password is not None:
                password = generate_password_hash(password)
            else:
                password = user.password

            if approved is not None:
                if user.role == 'admin':
                    raise BadRequest('admin user can not be approved')
                if approved is True:
                    user.approved = True
                else:
                    user.approved = False

            if image is not None:
                try:
                    if user.image_name == 'default.png':
                        image_name = secrets.token_hex(4) + '.png'
                    else:
                        image_name = user.image_name

                    file_data = base64.b64decode(image)
                    filename = UPLOAD_FOLDER + '/images/users/' + image_name
                    # print('user image file to be saved:', filename)

                    img = Image.open(BytesIO(file_data))
                    img.resize((200, 200))
                    img.save(filename, format='PNG')

                except:
                    raise InternalError('error saving image')

            user.name = name.title()
            user.password = password
            user.email = email
            user.image_name = image_name
            user.updated_timestamp = datetime.now(ZoneInfo('Asia/Kolkata'))

            try:
                db.session.add(user)
                cache.clear()
                db.session.commit()
                cache.clear()
            except:
                raise InternalError(message="error in updating User")

            data = jsonify(user.to_dict())
            return make_response(data, 200)

    @jwt_required()
    def delete(self, username=None):
        if username is None:
            raise BadRequest("User name is missing")
        else:
            user = User.query.filter_by(username=username).first()
            if user is None:
                raise NotFound(message="User not found")

            if user.username == 'admin':
                raise AuthorizationError('admin user can not be deleted')
            try:
                db.session.delete(user)
                cache.clear()
                db.session.commit()
                cache.clear()

                if user.image_name != 'default.png':
                    filename = UPLOAD_FOLDER + '/images/users/' + user.image_name
                    if os.path.isfile(filename):
                        try:
                            os.remove(filename)
                        except:
                            raise InternalError('deleting the image file')
            except:
                raise InternalError(message="Error deleting User")

        return f"user {user.name} deleted successfully", 200


section_request_parse = reqparse.RequestParser(bundle_errors=True)
section_request_parse.add_argument("name", type=str, required=True)
section_request_parse.add_argument("approved", type=inputs.boolean)
section_request_parse.add_argument("request_type", type=str)
section_request_parse.add_argument("request_data", type=str)
class SectionAPI(Resource):
    '''Section Object for managing sections'''
    @jwt_required()
    @cache.cached(timeout=50)
    def get(self, section_id=None):
        if section_id is None:
            sections = Section.query.all()
            data = [section.to_dict() for section in sections]
            return make_response(data, 200)
        else:
            section = Section.query.filter_by(id=section_id).one_or_none()
            if section is None:
                raise NotFound("section not found")
            else:
                # print(section)
                return make_response(jsonify(section.to_dict()), 200)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        if user_id is None:
            raise NotFound("user id is missing in token")

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            raise NotFound("user not found")

        if user.role == 'admin':
            approved = True
        else:
            approved = False

        args = section_request_parse.parse_args(strict=True)
        name = args.get("name", None)
        if name is None:
            raise BadRequest("name not provided")
        name = name.capitalize()

        section = Section.query.filter_by(name=name).first()
        if section is not None:
            print("=== section already exists === ")
            raise BadRequest("section already exists")

        section = Section(
            name=name,
            request_type="add",
            request_data=name,
            approved=approved,
            created_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
            updated_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
        )

        if section is None:
            raise InternalError(message="error creating section")

        try:
            db.session.add(section)
            cache.clear()
            db.session.commit()
            cache.clear()
        except:
            raise InternalError(message="error creating section")

        return make_response(section.to_dict(), 201)

    @jwt_required()
    def put(self, section_id):
        user_id = get_jwt_identity()
        if user_id is None:
            raise NotFound("user id is missing in token")
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            raise NotFound("user not found")

        if section_id is None:
            raise NotFound("section id is missing")

        section = Section.query.filter_by(id=section_id).first()
        if section is None:
            return NotFound("section not found")
        else:
            args = section_request_parse.parse_args(strict=True)
            # print(args)

            name = args.get("name", None)
            if name is None:
                raise BadRequest("name is not provided")
            else:
                name = name.capitalize()

            request_type = args.get("request_type", None)
            request_data = args.get("request_data", None)
            approved = args.get("approved", None)

            if approved is True and user.role != 'admin':
                raise BadRequest('only admin can approve sections')

            # section.name = name

            if user.role == 'admin':
                if approved is not None:
                    if section.approved is False:
                        if approved is True:
                            if section.request_type == 'delete':
                                return self.delete(section.id)
                            elif section.request_type == 'add' or section.request_type == 'edit':
                                section.name = section.request_data
                                section.approved = True
                            else:
                                raise BadRequest("section request type is invalid")
                        else:
                            section.name=name
                            section.approved = True
                    else:
                        raise BadRequest("section is already approved")
                else:
                    section.name=request_data
                    section.approved = True
            elif user.role == 'manager':
                if section.approved is False:
                    raise BadRequest("section is already in approval stage")
                if request_type == 'edit':
                    if section.name == request_data:
                        section.approved = True
                    else:
                        section.request_type = request_type
                        section.request_data = request_data
                        section.approved = False
            else:
                raise AuthorizationError(message="only admin can approve sections")

            section.updated_timestamp = datetime.now(ZoneInfo('Asia/Kolkata'))

            try:
                db.session.add(section)
                cache.clear()
                db.session.commit()
                cache.clear()
            except:
                raise InternalError(message="error in updating section")

            return make_response(jsonify(section.to_dict()), 200)

    @jwt_required()
    def delete(self, section_id):
        if id is None:
            raise BadRequest("section id is missing")

        user_id = get_jwt_identity()
        if user_id is None:
            raise NotFound("user id is missing in token")
        else:
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                raise NotFound("user not found")

        section = Section.query.filter_by(id=section_id).first()
        if section is None:
            raise NotFound(message="section not found")

        if user.role == 'manager':
            section.request_type='delete'
            section.approved=False
            try:
                db.session.add(section)
                cache.clear()
                db.session.commit()
                cache.clear()
            except:
                raise InternalError(message="error requesting section deletion")

            return f'section {section.name} deletion sent for review successfully', 200
        elif user.role == 'admin':
            try:
                db.session.delete(section)
                cache.clear()
                db.session.commit()
                cache.clear()
            except:
                raise InternalError(message="error deleting section")
        else:
            raise AuthorizationError(message="only admin can delete sections")

        return f'section {section.name} deleted successfully', 200


def valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M")

product_request_parse = reqparse.RequestParser(bundle_errors=True)
product_request_parse.add_argument("name", type=str, required=True)
product_request_parse.add_argument("description", type=str, required=True)
product_request_parse.add_argument("unit", type=str, required=True, default="piece")
product_request_parse.add_argument("price", type=int, required=True)
product_request_parse.add_argument("stock", type=int, required=True)
product_request_parse.add_argument("expiry_date", type=valid_date, required=True)
product_request_parse.add_argument("image_name", type=str)
product_request_parse.add_argument("image", type=str)

class ProductAPI(Resource):
    '''Product Object for managing products'''

    @cache.cached(timeout=50)
    def get(self, section_id=None, product_id=None):
        if section_id is None:
            products = Product.query.all()
            data = [product.to_dict() for product in products]
            return make_response(data, 200)
        else:
            section=Section.query.filter_by(id=section_id).first()
            if section is None:
                raise NotFound("Section not found")

        if product_id is None:
            products = Product.query.filter_by(section_id=section_id).all()
            data = [product.to_dict() for product in products]
            return make_response(data, 200)
        else:
            product = Product.query.filter_by(section_id=section.id, id=product_id).first()
            if product is None:
                raise NotFound("Product not found")
            else:
                data = jsonify(product.to_dict())
                return make_response(data, 200)

    @jwt_required()
    def post(self, section_id):
        if section_id is None:
            raise BadRequest("Section id is missing")
        else:
            section=Section.query.filter_by(id=section_id).first()
            if section is None:
                raise NotFound("Section not found")

        args = product_request_parse.parse_args(strict=True)
        # print(args)
        name = args.get("name", None)
        description = args.get("description", None)
        unit = args.get("unit", None)
        price = args.get("price", None)
        stock = args.get("stock", None)
        expiry_date = args.get("expiry_date", None)
        image_name = args.get("image_name", None)
        image = args.get("image", None)

        if name is None:
            raise BadRequest("name not provided")
        if description is None:
            raise BadRequest("description not provided")
        if unit is None:
            raise BadRequest("unit not provided")
        if price is None:
            raise BadRequest("price not provided")
        if stock is None:
            raise BadRequest("stock not provided")
        if expiry_date is None:
            raise BadRequest("expiry date not provided")

        if image_name is None:
            image_name = 'default.png'
        else:
            image_name = secrets.token_hex(4) + '.png'


        product = Product(
            name=name,
            description=description,
            unit=unit,
            price=price,
            stock=stock,
            stock_sold = 0,
            stock_available=stock,
            expiry_date=expiry_date,
            image_name=image_name,
            section_id=section_id,
            created_timestamp=datetime.now(),
            updated_timestamp=datetime.now(),
        )
        if product is None:
            raise InternalError(message="error creating product")

        db.session.add(product)
        db.session.flush()

        # print(image_name, image)
        if image_name is not None and image is not None:
            try:
                if image_name == "":
                    raise BadRequest("image_name is empty")

                # image_name = image_name.split('.')[0] + '_' + str(product.id) + '.png'
                product.image_name = image_name

                file_data = base64.b64decode(image)
                filename= UPLOAD_FOLDER + '/images/products/' + image_name
                # print('Image filename to be saved: ', filename)

                # with open(filename, 'wb') as f:
                #     f.write(file_data)

                img = Image.open(BytesIO(file_data))
                img.resize((360, 360))
                img.save(filename, format='PNG')

            except:
                raise InternalError(message="Error in saving image")
        else:
            image_name = 'default.png'
            product.image_name = image_name

        try:
            db.session.add(product)
            cache.clear()
            db.session.commit()
            cache.clear()
        except:
            raise InternalError(message="error creating product")

        data = jsonify(product.to_dict())
        return make_response(data, 201)

    @jwt_required()
    def put(self, section_id, product_id):
        if section_id is None:
            raise BadRequest("section id is missing")
        else:
            section=Section.query.filter_by(id=section_id).first()
            if section is None:
                raise NotFound("section not found")

        if product_id is None:
            raise BadRequest("product id is missing")
        else:
            args=product_request_parse.parse_args(strict=True)
            # print(args)
            product=Product.query.filter_by(section_id=section_id, id=product_id).first()
            if product is None:
                raise NotFound("product not found")
            else:
                name = args.get("name", None)
                description = args.get("description", None)
                unit = args.get("unit", None)
                price = args.get("price", None)
                stock = args.get("stock", None)
                expiry_date = args.get("expiry_date", None)
                image = args.get("image", None)
                image_name = args.get("image_name", None)

                print('image_name: ', image_name, 'product imagename:', product.image_name)
                if image_name is None:
                    image_name = product.image_name

                if image is not None:
                    try:
                        # image_name = image_name.split('.')[0] + '_' + str(user.id) + '.png'

                        if product.image_name == 'default.png':
                            image_name = secrets.token_hex(4) + '.png'
                        else:
                            image_name = product.image_name

                        file_data = base64.b64decode(image)
                        filename= UPLOAD_FOLDER + '/images/products/' + image_name
                        # print('Image filename to be saved: ', filename)

                        # with open(filename, 'wb') as f:
                        #     f.write(file_data)
                        #     os.sync()

                        img = Image.open(BytesIO(file_data))
                        img = img.resize((360, 360))
                        img.save(filename, format='PNG')
                    except:
                        raise InternalError(message="Error in saving image")

                if (stock < product.stock_sold):
                    raise BadRequest("new stock can not be less than stock sold")

                if (stock > product.stock):
                    product.stock_available = product.stock_available + (stock - product.stock)
                elif (stock < product.stock):
                    product.stock_available = product.stock_available - (product.stock - stock)

                product.name = name
                product.description = description
                product.unit = unit
                product.price = price
                product.stock = stock
                product.expiry_date = expiry_date
                product.image_name = image_name
                product.section_id = section_id
                product.updated_timestamp=datetime.now(ZoneInfo('Asia/Kolkata'))

                try:
                    db.session.add(product)
                    cache.clear()
                    db.session.commit()
                    cache.clear()
                except:
                    raise InternalError(message="Error in updating product")

                data = jsonify(product.to_dict())
                return make_response(data, 200)

    @jwt_required()
    def delete(self, section_id, product_id):
        if section_id is None:
            raise BadRequest("section id is missing")
        if product_id is None:
            raise BadRequest("product id is missing")
        else:
            product=Product.query.filter_by(section_id=section_id, id=product_id).first()
            if product is None:
                raise NotFound("product not found")
            try:
                image_name = product.image_name
                db.session.delete(product)
                cache.clear()
                db.session.commit()
                cache.clear()

                if image_name != 'default.png':
                    filename= UPLOAD_FOLDER + '/images/products/' + image_name
                    if os.path.isfile(filename):
                        try:
                            os.remove(filename)
                        except:
                            raise InternalError('deleting the image file')
            except:
                raise InternalError(message="error deleting product")

        return f"product {product.name} deleted successfully", 200
def valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M")

order_request_parse = reqparse.RequestParser(bundle_errors=True)
order_request_parse.add_argument("name", type=str, required=True)
order_request_parse.add_argument("address", type=str, required=True)
order_request_parse.add_argument("phone_number", type=int, required=True)
order_request_parse.add_argument("items",type=str,action='append',location='json', required=True)
order_request_parse.add_argument("total_amount", type=int, required=True)
order_request_parse.add_argument("delivery_date", type=valid_date, required=True)
# order_request_parse.add_argument("user_id", type=int)
class OrderAPI(Resource):
    '''Order Object for managing orders'''
    # @marshal_with(order_response_fields)
    @jwt_required()
    @cache.cached(timeout=50)
    def get(self, id=None):
        user_id = get_jwt_identity()
        if user_id is None:
            raise NotFound("user id is missing")
        if id is None:
            orders = Order.query.filter_by(user_id=user_id).all()
            data = [order.to_dict() for order in orders]
            return make_response(data, 200)
        else:
            order = Order.query.filter_by(user_id=user_id, id=id).first()
            if order is None:
                raise NotFound("order not found")
            else:
                return make_response(order.to_dict(), 200)

    # @marshal_with(order_response_fields)
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        print(user_id)
        if user_id is None:
            raise BadRequest("user id is missing/not logged in")
        else:
            user=User.query.filter_by(id=user_id).first()
            print(user)
            if user is None:
                raise NotFound("user not found")

            args = order_request_parse.parse_args()
            # print(args)
            name=args.get('name', None)
            address=args.get('address', None)
            phone_number=args.get('phone_number', None)
            items=args.get('items', None)
            total_amount=args.get('total_amount', None)
            delivery_date=args.get('delivery_date', None)

            if name is None:
                raise BadRequest('name not provided')
            if address is None:
                raise BadRequest('address not provided')
            if phone_number is None:
                raise BadRequest('phone number not provided')
            if items is None:
                raise BadRequest('items not provided')
            elif items == []:
                raise BadRequest('items are empty')
            if total_amount is None:
                raise BadRequest('total amount not provided')
            if delivery_date is None:
                raise BadRequest('delivery date not provided')

            order = Order(
                name = name,
                address=address,
                phone=phone_number,
                email='test@test.com',
                payment_mode='cod',
                total_amount=total_amount,
                delivery_date=delivery_date,
                user_id=user.id,
                created_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
            )

            db.session.add(order)
            db.session.flush()

            items_list = []
            product_list = []
            for item in json.loads(items[0]):
                product = Product.query.filter_by(id=item['id']).first()
                cache.clear()
                # print('name:',product.name, 'stock:', product.stock, 'stock available:', product.stock_available, 'stock sold:', product.stock_sold)
                if product.stock_available < item['quantity']:
                    raise BadRequest(f"quantity requested  for product {product.name} is more than stock available(available: {product.stock_available})")

                new_item = Item(
                    quantity=item['quantity'],
                    product_id=item['id'],
                    order_id=order.id,
                    created_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
                    updated_timestamp=datetime.now(ZoneInfo('Asia/Kolkata')),
                )
                product.stock_available = product.stock_available - item['quantity']
                product.stock_sold = product.stock_sold + item['quantity']
                if (product.stock != (product.stock_available + product.stock_sold)):
                    raise InternalError(message="error in updating stock")

                # cache.clear()
                # print('name:', product.name, 'stock:', product.stock, 'stock available:', product.stock_available, 'stock sold:', product.stock_sold)
                items_list.append(new_item)
                product_list.append(product)

            try:
                db.session.add_all(items_list)
                db.session.add_all(product_list)
                db.session.add(order)
                cache.clear()
                db.session.commit()
                cache.clear()
            except:
                raise InternalError(message="error creating order")
            return make_response(order.to_dict(), 201)

    @jwt_required()
    def put(self,id, user_id, items):
        return "put method not implemented", 501

    @jwt_required()
    def delete(self, id):
        if id is None:
            raise BadRequest("Order id is missing")

        order=Order.query.filter_by(id=id).first()
        try:
            db.session.delete(order)
            cache.clear()
            db.session.commit()
            cache.clear()
        except:
            raise InternalError(message="Error deleting order")
        return "Order deleted successfully", 200


# End of File
