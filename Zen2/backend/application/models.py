from datetime import datetime
import os
import base64

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref,relationship
from werkzeug.security import generate_password_hash
from .db import db
from .config import UPLOAD_FOLDER



class User(db.Model):
    '''User Model'''
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(32), nullable=False, default="user")
    image_name = db.Column(db.String(32), default="default.png")
    created_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())
    updated_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())

    orders = db.relationship("Order", backref="user", cascade="all, delete-orphan")

    def to_dict(self):
        self.image=None
        image_file= UPLOAD_FOLDER + '/images/users/' + self.image_name
        if os.path.isfile(image_file):
            with open(image_file, 'rb') as f:
                self.image = base64.b64encode(f.read()).decode('utf-8')

        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "approved": self.approved,
            "role": self.role,
            "image_name": self.image_name,
            "image":self.image,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            # "orders": [order.to_dict() for order in self.orders],
        }

    def __repr__(self) -> str:
        return self.username


class Section(db.Model):
    '''Section Model'''
    __tablename__ = "section"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False) 
    request_type = db.Column(db.String(32))
    request_data = db.Column(db.String(64))
    approved = db.Column(db.Boolean, nullable=False, default=False)
    created_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())
    updated_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())

    books = db.relationship("Book", backref="section", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "approved": self.approved,
            "request_type": self.request_type,
            "request_data": self.request_data,
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            # "products": [product.to_dict() for product in self.products],
        }


class Book(db.Model):
    '''Book Model'''
    __tablename__ = "book"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String(32), nullable=False)
    image_name = db.Column(db.String(64), default="default.png")
    status = db.Column(db.String(32), default="available")
    date_issued = db.Column(db.DateTime(timezone=True))
    feedback = db.relationship("Feedback", backref="book", cascade="all, delete-orphan")
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)

    def to_dict(self):
        self.image=None
        image_file= UPLOAD_FOLDER + '/images/books/' + self.image_name
        if os.path.isfile(image_file):
            with open(image_file, 'rb') as f:
                self.image = base64.b64encode(f.read()).decode('utf-8')
        # Check if the PDF file exists

        section = Section.query.filter_by(id=self.section_id).first()

        return {
            "id": self.id,
            "name": self.name,
            "section_name": section.name,
            "description": self.description,
            "price": self.price,
            "status": self.status,
            "author": self.author,
            "date_issued":self.date_issued,
            "image_name": self.image_name,
            "image": self.image,
            "section_id": self.section_id,
        }

class Feedback(db.Model):
    '''Feedback Model'''
    __tablename__ = "feedback"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    stars =  db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String())

    def to_dict(self):
        '''to_dict'''
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "stars":self.stars,
            "comment":self.comment,
        }
    

class Item(db.Model):
    '''Item Model'''
    __tablename__ = "item"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    created_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())
    updated_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())

    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)

    def to_dict(self):
        book = Book.query.filter_by(id=self.book_id).first()
        self.image=None
        image_file= UPLOAD_FOLDER + '/images/books/' + book.image_name
        if os.path.isfile(image_file):
            with open(image_file, 'rb') as f:
                self.image = base64.b64encode(f.read()).decode('utf-8')
        return {
            "id": self.id,
            "book": book.to_dict(),
            "created_timestamp": self.created_timestamp,
            "updated_timestamp": self.updated_timestamp,
            "book_id": self.book_id,
            "order_id": self.order_id,
        }
class Request(db.Model):
    '''Request Model'''
    __tablename__ = "request"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    book_status = db.Column(db.Integer, db.ForeignKey("book.status"), nullable=False)

    def to_dict(self):
        book = Book.query.filter_by(id=self.book_id).first()
        return {
            "id": self.id,
            "book": book.to_dict(),
            "created_timestamp": self.created_timestamp,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book_status": self.book_status,
        }
    

class Order(db.Model):
    '''Order Model'''
    __tablename__ = "order"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship("Item", backref="order",  cascade="all,delete-orphan")
    created_timestamp = db.Column(
        db.DateTime(timezone=True), nullable=False, default=datetime.now())
    
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    payment_mode=db.Column(db.String(16), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        '''to_dict'''
        return {
            "id": self.id,
            "total_amount": self.total_amount,
            "name":self.name,
            "email":self.email,
            "payment_mode":self.payment_mode,
            "items": [item.to_dict() for item in self.items],
            "created_timestamp": self.created_timestamp,
            "user_id": self.user_id,
        }

class Issue(db.Model):
    '''Issue Model'''
    __tablename__ = "issue"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False,unique=True)
    issue_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    return_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now())
    status = db.Column(db.String(), nullable=False)


    def to_dict(self):
        '''to_dict'''
        book = Book.query.filter_by(id=self.book_id).first()
        section = Section.query.filter_by(id=book.section_id)
        return {
            "id": self.id,
            "book": book.to_dict(),
            "issue_date": self.issue_date,
            "return_date": self.return_date,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "status": self.status,
            "book_name": book.name,
            "section": section,
            "author": book.author,
            
        }


def create_initial_data(db):
    '''create admin user'''
    admin = User(
        name="Admin",
        username="admin",
        email="admin@butti.com",
        password=generate_password_hash("admin"),
        role="admin",
        approved = True,
        image_name = "default.png",
        created_timestamp=datetime.now(),
        updated_timestamp=datetime.now(),
    )
    
    section_types = [
        "Fiction",
        "Non-fiction",
        "Mystery/Thriller",
        "Science Fiction/Fantasy",
        "Romance",
        "Biography/Autobiography",
        "History",
        "Self-help/Personal Development",
        "Poetry"
    ]
    descriptions = {
        "Fiction": "Engage your imagination with captivating stories that transport you to different worlds and times.",
        "Non-fiction": "Explore real-life events, facts, and information on a variety of topics from history to science.",
        "Mystery/Thriller": "Keep on the edge of your seat with suspenseful plots and intriguing mysteries waiting to be solved.",
        "Science Fiction/Fantasy": "Dive into realms of the impossible and discover imaginative worlds filled with futuristic technology and magical creatures.",
        "Romance": "Experience the magic of love and passion as you follow characters on their journey to finding happiness.",
        "Biography/Autobiography": "Discover the lives of extraordinary individuals, from famous figures to ordinary people with remarkable stories.",
        "History": "Uncover the events and people that have shaped the world we live in today, from ancient civilizations to modern times.",
        "Self-help/Personal Development": "Empower yourself with practical advice and strategies for personal growth and self-improvement.",
        "Poetry": "Be inspired by the beauty of language and emotion expressed through the art of poetry, where words become a canvas for the soul."
    }

    book_samples = [
        {
            "name": "1984",
            "description": "A dystopian novel by George Orwell, portraying a totalitarian regime and the struggle for individual freedom",
            "price": 18,
            "author": "George Orwell",
            "image_name": "1984.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "American Psycho",
            "description": "American Psycho is a dark tale following Patrick Bateman, a wealthy banker in 1980s Manhattan, as he descends into violence and madness. It offers a critique of excess and moral decay in American society.",
            "price": 20,
            "author": "Bret Easton-Ellis",
            "image_name": "american_psycho.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "To Kill a Mockingbird",
            "description": "Harper Lee's classic novel addressing racial injustice and moral growth in the American South",
            "price": 15,
            "author": "Harper Lee",
            "image_name": "to_kill_a_mockingbird.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "Pride and Prejudice",
            "description": "Jane Austen's timeless romance exploring the societal norms and prejudices of early 19th-century England",
            "price": 22,
            "author": "Jane Austen",
            "image_name": "pride.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "The Great Gatsby",
            "description": "F. Scott Fitzgerald's portrayal of the American Dream and the decadence of the Jazz Age",
            "price": 25,
            "author": "F. Scott Fitzgerald",
            "image_name": "the_great_gatsby.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "The Catcher in the Rye",
            "description": "J.D. Salinger's novel following the disillusioned teenager Holden Caulfield through his adventures in New York City",
            "price": 17,
            "author": "J.D. Salinger",
            "image_name": "catcher.jpeg",
            "status": "available",
            "section_id": 1
        },
        {
            "name": "Sapiens: A Brief History of Humankind",
            "description": "Yuval Noah Harari's exploration of the history of Homo sapiens from the Stone Age to the present",
            "price": 30,
            "author": "Yuval Noah Harari",
            "image_name": "sapiens.jpeg",
            "status": "available",
            "section_id": 2
        },
        {
            "name": "Educated",
            "description": "Tara Westover's memoir recounting her journey from a survivalist family in Idaho to earning a PhD from Cambridge University",
            "price": 28,
            "author": "Tara Westover",
            "image_name": "educated.jpeg",
            "status": "available",
            "section_id": 2
        },
        {
            "name": "The Immortal Life of Henrietta Lacks",
            "description": "Rebecca Skloot's investigation into the life of Henrietta Lacks and the impact of her immortal cell line on medical research",
            "price": 25,
            "author": "Rebecca Skloot",
            "image_name": "immortal_life.jpeg",
            "status": "available",
            "section_id": 2
        },
        {
            "name": "Into the Wild",
            "description": "Jon Krakauer's non-fiction account of Christopher McCandless's journey into the Alaskan wilderness",
            "price": 20,
            "author": "Jon Krakauer",
            "image_name": "into_the_wild.jpeg",
            "status": "available",
            "section_id": 2
        },
        {
            "name": "The Girl with the Dragon Tattoo",
            "description": "Stieg Larsson's gripping thriller featuring investigative journalist Mikael Blomkvist and hacker Lisbeth Salander",
            "price": 22,
            "author": "Stieg Larsson",
            "image_name": "dragon.jpeg",
            "status": "available",
            "section_id": 3
        },
        {
            "name": "Gone Girl",
            "description": "Gillian Flynn's psychological thriller about a woman who goes missing on her fifth wedding anniversary",
            "price": 20,
            "author": "Gillian Flynn",
            "image_name": "gone_girl.jpeg",
            "status": "available",
            "section_id": 3
        },
        {
            "name": "The Da Vinci Code",
            "description": "Dan Brown's mystery thriller involving a symbologist and a cryptologist unraveling a secret society's ancient secrets",
            "price": 18,
            "author": "Dan Brown",
            "image_name": "da_vinci_code.jpeg",
            "status": "available",
            "section_id": 3
        },
        {
            "name": "The Silent Patient",
            "description": "Alex Michaelides's psychological thriller about a woman who shoots her husband and then stops speaking",
            "price": 25,
            "author": "Alex Michaelides",
            "image_name": "silent.jpeg",
            "status": "available",
            "section_id": 3
        },
        {
            "name": "Big Little Lies",
            "description": "Liane Moriarty's mystery novel set in a small Australian town, exploring the secrets and lies of its residents",
            "price": 23,
            "author": "Liane Moriarty",
            "image_name": "big_little_lies.jpeg",
            "status": "available",
            "section_id": 3
        },
        {
            "name": "Dune",
            "description": "Frank Herbert's epic science fiction novel set in a distant future where noble houses vie for control of a desert planet",
            "price": 28,
            "author": "Frank Herbert",
            "image_name": "dune.jpeg",
            "status": "available",
            "section_id": 4
        },
        {
            "name": "The Hobbit",
            "description": "J.R.R. Tolkien's fantasy novel following the journey of Bilbo Baggins as he accompanies a group of dwarves to reclaim their homeland",
            "price": 26,
            "author": "J.R.R. Tolkien",
            "image_name": "hobbit.jpeg",
            "status": "available",
            "section_id": 4
        },
        {
            "name": "Foundation",
            "description": "Isaac Asimov's science fiction classic depicting the rise and fall of a galactic empire and the efforts to preserve human knowledge",
            "price": 30,
            "author": "Isaac Asimov",
            "image_name": "foundation.jpeg",
            "status": "available",
            "section_id": 4
        },
        {
            "name": "Harry Potter and the Sorcerer's Stone",
            "description": "J.K. Rowling's first novel in the Harry Potter series, following the journey of a young wizard, Harry Potter",
            "price": 24,
            "author": "J.K. Rowling",
            "image_name": "harry.jpeg",
            "status": "available",
            "section_id": 4
        },
        {
            "name": "The Hunger Games",
            "description": "Suzanne Collins's dystopian novel set in a future where children fight to the death in a televised event",
            "price": 22,
            "author": "Suzanne Collins",
            "image_name": "hunger.jpeg",
            "status": "available",
            "section_id": 4
        },
        {
            "name": "The Notebook",
            "description": "Nicholas Sparks's romance novel depicting the enduring love between Noah Calhoun and Allie Nelson",
            "price": 20,
            "author": "Nicholas Sparks",
            "image_name": "notebook.jpeg",
            "status": "available",
            "section_id": 5
        },
        {
            "name": "Outlander",
            "description": "Diana Gabaldon's time-traveling romance novel featuring Claire Randall and Jamie Fraser in 18th-century Scotland",
            "price": 26,
            "author": "Diana Gabaldon",
            "image_name": "outlander.jpeg",
            "status": "available",
            "section_id": 5
        },
        {
            "name": "Me Before You",
            "description": "Jojo Moyes's novel about the relationship between a young caregiver and a quadriplegic man",
            "price": 21,
            "author": "Jojo Moyes",
            "image_name": "me_before_you.jpeg",
            "status": "available",
            "section_id": 5
        },
        {
            "name": "The Fault in Our Stars",
            "description": "John Green's novel following the love story between two teenagers, Hazel Grace Lancaster and Augustus Waters, both cancer patients",
            "price": 18,
            "author": "John Green",
            "image_name": "fault.jpeg",
            "status": "available",
            "section_id": 5
        },
        {
            "name": "Steve Jobs",
            "description": "Walter Isaacson's biography of Steve Jobs, co-founder of Apple Inc., offering insights into his life, career, and innovations",
            "price": 29,
            "author": "Walter Isaacson",
            "image_name": "steve.jpeg",
            "status": "available",
            "section_id": 6
        },
        {
            "name": "Becoming",
            "description": "Michelle Obama's memoir detailing her life from childhood to her time as First Lady of the United States",
            "price": 32,
            "author": "Michelle Obama",
            "image_name": "becoming.jpeg",
            "status": "available",
            "section_id": 6
        },
        {
            "name": "The Diary of a Young Girl",
            "description": "Anne Frank's diary documenting her experiences hiding from the Nazis during World War II",
            "price": 23,
            "author": "Anne Frank",
            "image_name": "diary.jpeg",
            "status": "available",
            "section_id": 6
        },
        {
            "name": "Long Walk to Freedom",
            "description": "Nelson Mandela's autobiography recounting his life and struggle against apartheid in South Africa",
            "price": 27,
            "author": "Nelson Mandela",
            "image_name": "long_walk.jpeg",
            "status": "available",
            "section_id": 6
        },
        {
            "name": "Bossypants",
            "description": "Tina Fey's memoir sharing her experiences in comedy, television, and motherhood",
            "price": 20,
            "author": "Tina Fey",
            "image_name": "bossypants.jpeg",
            "status": "available",
            "section_id": 6
        },
        {
            "name": "A People's History of the United States",
            "description": "Howard Zinn's alternative history of the United States, focusing on the experiences of marginalized groups",
            "price": 30,
            "author": "Howard Zinn",
            "image_name": "history_united.jpeg",
            "status": "available",
            "section_id": 7
        },
        {
            "name": "The Rise and Fall of the Third Reich",
            "description": "William L. Shirer's comprehensive history of Nazi Germany from its rise to power to its collapse",
            "price": 35,
            "author": "William L. Shirer",
            "image_name": "third_reich.jpeg",
            "status": "available",
            "section_id": 7
        },
        {
            "name": "Guns, Germs, and Steel",
            "description": "Jared Diamond's analysis of the factors that led to the dominance of certain civilizations throughout history",
            "price": 28,
            "author": "Jared Diamond",
            "image_name": "guns.jpeg",
            "status": "available",
            "section_id": 7
        },
        {
            "name": "The Wright Brothers",
            "description": "David McCullough's biography of Orville and Wilbur Wright, pioneers of aviation",
            "price": 25,
            "author": "David McCullough",
            "image_name": "wright.jpeg",
            "status": "available",
            "section_id": 7
        },
        {
            "name": "The Gulag Archipelago",
            "description": "Aleksandr Solzhenitsyn's account of the Soviet forced labor camp system and its impact on prisoners",
            "price": 32,
            "author": "Aleksandr Solzhenitsyn",
            "image_name": "gulag.jpeg",
            "status": "available",
            "section_id": 7
        },
        {
            "name": "The 7 Habits of Highly Effective People",
            "description": "Stephen R. Covey's guide to personal and professional effectiveness based on principles of fairness, integrity, and human dignity",
            "price": 26,
            "author": "Stephen R. Covey",
            "image_name": "habits.jpeg",
            "status": "available",
            "section_id": 8
        },
        {
            "name": "Atomic Habits",
            "description": "James Clear's book offering a framework for building good habits and breaking bad ones",
            "price": 24,
            "author": "James Clear",
            "image_name": "atomic.jpeg",
            "status": "available",
            "section_id": 8
        },
        {
            "name": "The Subtle Art of Not Giving a F*ck",
            "description": "Mark Manson's unconventional self-help book advocating a more honest and less sugar-coated approach to life",
            "price": 22,
            "author": "Mark Manson",
            "image_name": "subtle.jpeg",
            "status": "available",
            "section_id": 8
        },
        {
            "name": "Girl, Wash Your Face",
            "description": "Rachel Hollis's motivational book urging women to let go of lies and misconceptions that hold them back",
            "price": 20,
            "author": "Rachel Hollis",
            "image_name": "girl.jpeg",
            "status": "available",
            "section_id": 8
        },
        {
            "name": "You Are a Badass",
            "description": "Jen Sincero's guide to self-help and personal development, encouraging readers to embrace their inner badass",
            "price": 18,
            "author": "Jen Sincero",
            "image_name": "badass.jpeg",
            "status": "available",
            "section_id": 8
        },
        {
            "name": "Milk and Honey",
            "description": "Rupi Kaur's collection of poetry and prose exploring themes of love, loss, trauma, and healing",
            "price": 20,
            "author": "Rupi Kaur",
            "image_name": "rupi.jpeg",
            "status": "available",
            "section_id": 9
        },
        {
            "name": "The Sun and Her Flowers",
            "description": "Rupi Kaur's second collection of poetry reflecting on growth, self-love, and resilience",
            "price": 22,
            "author": "Rupi Kaur",
            "image_name": "sun.jpeg",
            "status": "available",
            "section_id": 9
        },
        {
            "name": "Leaves of Grass",
            "description": "Walt Whitman's collection of poetry celebrating the beauty of nature, democracy, and the human spirit",
            "price": 18,
            "author": "Walt Whitman",
            "image_name": "leaves.jpeg",
            "status": "available",
            "section_id": 9
        },
        {
            "name": "The Waste Land",
            "description": "T.S. Eliot's modernist poem exploring themes of disillusionment and cultural decay in post-World War I society",
            "price": 19,
            "author": "T.S. Eliot",
            "image_name": "wasteland.jpeg",
            "status": "available",
            "section_id": 9
        },
        {
            "name": "Ariel",
            "description": "Sylvia Plath's collection of confessional poetry exploring themes of femininity, mental illness, and mortality",
            "price": 21,
            "author": "Sylvia Plath",
            "image_name": "ariel.jpeg",
            "status": "available",
            "section_id": 9
        },
        {
            "name": "Eleanor & Park",
            "description": "Set in the 1980s, this novel tells the story of two misfit teenagers who bond over music and comics. Despite their differences, they develop a deep connection that helps them navigate family, friendship, and first love.",
            "price": 18,
            "author": "Rainbow Rowell",
            "image_name": "eleanor.jpeg",
            "status": "available",
            "section_id": 5
        },
        {
            "name": "Quiet: The Power of Introverts in a World That Can't Stop Talking",
            "description": "In this book, Susan Cain explores the power of introverts in a society that values extroversion. Drawing on research in psychology and neuroscience, Cain argues that introverts bring unique strengths to workplaces, relationships, and communities.",
            "price": 24,
            "author": "Susan Cain",
            "image_name": "quiet.jpeg",
            "status": "available",
            "section_id": 2
        }
    ]



    setions = []
    books = []
    for section_type in section_types:
        section = Section(
            name=section_type,
            request_type="GET",
            description= descriptions[section_type],
            request_data="",
            approved=True,
            created_timestamp=datetime.now(),
            updated_timestamp=datetime.now(),
        )
        setions.append(section)
    for book_data in book_samples:
        book = Book(
            name=book_data["name"],
            description=book_data["description"],
            price=book_data["price"],
            author=book_data["author"],
            image_name=book_data["image_name"],
            status=book_data["status"],
            section_id=book_data["section_id"]
        )
        books.append(book)

    # Commit changes to the database
    db.session.add_all(books)
    db.session.add_all(setions)
    db.session.add(admin)
    db.session.commit()

# End of File 

