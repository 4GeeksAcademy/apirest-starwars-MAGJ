import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorite

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route("/")
def sitemap():
    return generate_sitemap(app)


def get_current_user():
  
    return User.query.get(1)

#get people
@app.route("/people", methods=["GET"])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_people(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "People not found"}), 404
    return jsonify(person.serialize()), 200


# get planets
@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200



@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


# get users
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


# get/users/favorites
@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "Current user (id=1) not found. Create it in Admin."}), 404

    favorites = Favorite.query.filter_by(user_id=user.id).all()
    return jsonify([f.serialize() for f in favorites]), 200


#post favorite/planet
@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "Current user (id=1) not found. Create it in Admin."}), 404

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    exists = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id).first()
    if exists:
        return jsonify({"msg": "Planet already in favorites"}), 409

    fav = Favorite(user_id=user.id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added", "favorite": fav.serialize()}), 201


# post favorite/people
@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "Current user (id=1) not found. Create it in Admin."}), 404

    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "People not found"}), 404

    exists = Favorite.query.filter_by(
        user_id=user.id, people_id=people_id).first()
    if exists:
        return jsonify({"msg": "People already in favorites"}), 409

    fav = Favorite(user_id=user.id, people_id=people_id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"msg": "Favorite people added", "favorite": fav.serialize()}), 201


# delete favorte/planet
@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "Current user (id=1) not found. Create it in Admin."}), 404

    fav = Favorite.query.filter_by(
        user_id=user.id, planet_id=planet_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200


# delete favorite/people
@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    user = get_current_user()
    if user is None:
        return jsonify({"msg": "Current user (id=1) not found. Create it in Admin."}), 404

    fav = Favorite.query.filter_by(
        user_id=user.id, people_id=people_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite people not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite people deleted"}), 200


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
