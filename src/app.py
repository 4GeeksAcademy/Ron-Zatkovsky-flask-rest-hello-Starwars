"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Favorites,People,Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def create_user():
    username=request.json["username"]
    password=request.json["password"]
    user1=User(username=username,password=password)
    db.session.add(user1)
    db.session.commit()
    response_body = {
        "msg": "Hello, user added "+username
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def all_users():
    users=User.query.all()
    all_users=list(map(lambda x: x.serialize(),users))
    return jsonify(all_users),200

@app.route('/users/favorites',methods=['GET'])
def get_favs():
    favs=Favorites.query.all()
    all_favs=list(map(lambda x: x.serialize(),favs))
    return jsonify(all_favs),200

@app.route('/favorite/planet/',methods=['POST'])
def add_fav():
    new_fav=Favorites(
        name=request.json["name"],
        category=request.json["category"],
        user_id=request.json["user_id"],
        planets_id=request.json["planets_id"],
    )
    db.session.add(new_fav)
    db.session.commit()
    favs=Favorites.query.all()
    return jsonify(list(map(lambda x: x.serialize(),favs)))

@app.route('/users/planets',methods=["POST"])
def add_planet():
    new_planet=Planets(
            name= request.json['name'],
            climate= request.json['climate'],
            gravity= request.json['gravity'],
            population= request.json['population'],
            terrain= request.json['terrain']
    )
    db.session.add(new_planet)
    db.session.commit()
    planets=Planets.query.all()
    return jsonify(list(map(lambda x: x.serialize(),planets)))

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
