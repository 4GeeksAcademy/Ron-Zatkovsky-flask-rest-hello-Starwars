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
    user=User.query.get(1)
    return jsonify(user.serialize()),200

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

@app.route('/favorite',methods=['POST'])
def add_fav():
    if request.json['category']=='planets':
        new_entity=Planets(
            name= request.json["name"],
            climate= request.json["climate"],
            gravity= request.json["gravity"],
            population= request.json["population"],
            terrain= request.json["terrain"],
        )
        db.session.add(new_entity)
        db.session.commit()
        planets_info=Planets.query.filter_by(name=request.json["name"]).first()
        new_fav=Favorites(
            name=request.json["name"],
            category=request.json["category"],
            user_id=request.json["user_id"],
            planets_id=planets_info.id,
        )
    elif request.json['category']=='people':
        new_entity=People(
            name=request.json["name"],
            gender=request.json["gender"],
            birth_year=request.json["birth_year"],
            height=request.json["height"],
            mass=request.json["mass"],
        )
        db.session.add(new_entity)
        db.session.commit()
        people_info=People.query.filter_by(name=request.json["name"]).first()
        new_fav=Favorites(
            name=request.json["name"],
            category=request.json["category"],
            user_id=request.json["user_id"],
            people_id=people_info.id,
        )
    # elif request.json['category']=='vehicles':
    #     new_entity=Vehicles(
            
    #     )
    #     new_fav=Favorites(
    #         name=request.json["name"],
    #         category=request.json["category"],
    #         user_id=request.json["user_id"],
    #         vehicles_id=request.json["entity_id"],
    #     )
    db.session.add(new_fav)
    db.session.commit()
    favs=Favorites.query.all()
    return jsonify(list(map(lambda x: x.serialize(),favs)))

@app.route('/favorite/<string:category>/<int:entity_id>/<int:user_id>',methods=["DELETE"])
def del_fav(category,entity_id,user_id):
    if(category=='planets'):
        record=Favorites.query.filter_by(category=category,planets_id=entity_id,user_id=user_id).first()
        entity=Planets.query.filter_by(id=entity_id).first()
        
    elif(category=='people'):
        record=Favorites.query.filter_by(category=category,people_id=entity_id,user_id=user_id).first()
        entity=People.query.filter_by(id=entity_id).first()
    db.session.delete(record)
    db.session.delete(entity)
    db.session.commit()
    return "Deleted "+entity.name

@app.route('/planets',methods=["GET"])
def get_planets():
    query=Planets.query.all()
    planets=list(map(lambda x: x.serialize(),query))
    return jsonify(planets)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
