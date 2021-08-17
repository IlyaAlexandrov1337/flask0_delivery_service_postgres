from csv import DictReader
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


meals_to_order_table = db.Table('meals_to_order',
    db.Column('meal_id', db.Integer, db.ForeignKey('meals.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    orders = db.relationship("Order", back_populates="user", uselist=False)



class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)
    category = db.relationship("Category", back_populates="meals", uselist=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    orders = db.relationship("Order", secondary=meals_to_order_table, back_populates="meals")


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    meals = db.relationship("Meal", back_populates="category")


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    sum = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    user = db.relationship("User", back_populates="orders", uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    meals = db.relationship("Meal", secondary=meals_to_order_table, back_populates="orders")


if __name__ == '__main__':

    with open('raw_database/categories.csv', encoding='UTF8') as file:
        reader = DictReader(file)
        for row in reader:
            category = Category(id=row['id'], title=row['title'])
            db.session.add(category)
        db.session.commit()

    with open('raw_database/meals.csv', encoding='UTF8') as file:
        reader = DictReader(file)
        for row in reader:
            meal = Meal(id=row['id'], title=row['title'], price=row['price'], description=row['description'],
                        picture=f"static/{row['picture']}", category=Category.query.get(int(row['category_id'])))
            db.session.add(meal)
        db.session.commit()