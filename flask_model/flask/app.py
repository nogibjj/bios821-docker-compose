from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
model_api = os.getenv('MODEL_URL')
db = SQLAlchemy(app)

class Restaurant(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False, nullable=False)
  cuisine = db.Column(db.String(100), unique=False, nullable=True)

  def __init__(self, name, cuisine):
    self.name = name
    self.cuisine = cuisine

  def as_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, unique=False, nullable=False)
    review = db.Column(db.String(200), unique=False, nullable=True)
    label = db.Column(db.String(20), unique=False, nullable=True)
    score = db.Column(db.Float, unique=False, nullable=False)

    def __init__(self, restaurant_id, review, label, score):
        self.restaurant_id = restaurant_id
        self.review = review
        self.label = label
        self.score = score

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


db.create_all()


@app.route('/restaurants/<id>', methods=['GET'])
def get_restaurant(id):
  return jsonify(Restaurant.query.get(id).as_dict())


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
  restaurants = []
  for r in db.session.query(Restaurant).all():
    restaurants.append(r.as_dict())
  return jsonify(restaurants)


@app.route('/restaurants', methods=['POST'])
def create_restaurant():
  body = request.get_json()
  db.session.add(Restaurant(body['name'], body['cuisine']))
  db.session.commit()
  return f'Restaurant {body["name"]} added.'


@app.route('/reviews/<restaurant_id>', methods=['GET'])
def get_restaurant_reviews(restaurant_id):
  reviews = []
  for r in db.session.query(Review).all():
      if r.restaurant_id == int(restaurant_id):
          reviews.append(r.as_dict())
  return jsonify(reviews)


@app.route('/reviews', methods=['GET'])
def get_all_reviews():
  reviews = []
  for r in db.session.query(Review).all():
      reviews.append(r.as_dict())
  return jsonify(reviews)


@app.route('/reviews', methods=['POST'])
def create_review():
  body = request.get_json()
  print(model_api)
  rating = requests.post(model_api,
                         json={'review': body['review']}).json()
  db.session.add(Review(int(body['restaurant_id']),
                        body['review'],
                        rating['label'],
                        float(rating['score'])))
  db.session.commit()
  return f'{rating["label"]} review added.'
