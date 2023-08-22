import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, FavoritePlanet, FavoritePeople

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

# Listar todos los registros de people en la base de datos
@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    people = [{"id": person.id, "name": person.name} for person in people_list]
    return jsonify(people)

# Listar la información de una sola people
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    return jsonify({"id": person.id, "name": person.name})

# Listar los registros de planets en la base de datos
@app.route('/planets', methods=['GET'])
def get_planets():
    planets_list = Planet.query.all()
    planets = [{"id": planet.id, "name": planet.name} for planet in planets_list]
    return jsonify(planets)

# Listar la información de un solo planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    return jsonify({"id": planet.id, "name": planet.name})

# Listar todos los usuarios del blog
@app.route('/users', methods=['GET'])
def get_users():
    users_list = User.query.all()
    users = [{"id": user.id, "username": user.username} for user in users_list]
    return jsonify(users)

# Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    
    user = User.query.get(1)  
    if user is None:
        raise APIException("User not found", status_code=404)
    
    favorites = {
        "favorite_planets": [{"planet_id": fav.planet_id} for fav in user.favorite_planets],
        "favorite_people": [{"people_id": fav.people_id} for fav in user.favorite_people]
    }
    return jsonify(favorites)

# Añade un nuevo planet favorito al usuario actual
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
 
    user = User.query.get(1) 
        raise APIException("User not found", status_code=404)
    
    favorite = FavoritePlanet(user_id=user.id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({"message": "Planet added to favorites"})

# Añade una nueva people favorita al usuario actual
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
   
    user = User.query.get(1)  
    if user is None:
        raise APIException("User not found", status_code=404)
    
    favorite = FavoritePeople(user_id=user.id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({"message": "People added to favorites"})

# Elimina un planet favorito con el id = planet_id
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):

    user = User.query.get(1) 
    if user is None:
        raise APIException("User not found", status_code=404)
    
    favorite = FavoritePlanet.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if favorite is not None:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites"})
    else:
        raise APIException("Favorite planet not found", status_code=404)


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    
    user = User.query.get(1)  
        raise APIException("User not found", status_code=404)
    
    favorite = FavoritePeople.query.filter_by(user_id=user.id, people_id=people_id).first()
    if favorite is not None:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "People removed from favorites"})
    else:
        raise APIException("Favorite people not found", status_code=404)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
