from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
from secrets_1 import MONGODB_URI, JWT_SECRET_KEY
from hashlib import sha256
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)
from helpers import serialize_mongo_doc
from bson.objectid import ObjectId
from datetime import timedelta, datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config["MONGO_URI"] = MONGODB_URI
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

mongo = PyMongo(app)
jwt = JWTManager(app)


@app.route("/")
def home():
    return "Hello niggas"


@app.route("/login", methods=["POST"])
def login():
    print(request.form)
    email = request.form["email"]
    password = request.form["password"]
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    print(password_hash)
    doc = mongo.db.get_collection("users").find_one(
        {"email": email, "password": password_hash}
    )
    if doc is not None:
        access_key = create_access_token(identity=doc["username"])
        curDate = datetime.now()
        expDate = curDate + timedelta(days=1)
        return {
            "message": "Successful login",
            "access_token": access_key,
            "expires_at": datetime.isoformat(expDate),
        }
    else:
        return {"message": "Login failed"}, 401


@app.route("/members", methods=["GET", "POST"])
@jwt_required()
def members():
    if request.method == "GET":
        members = mongo.db.get_collection("members").find()
        list_members = list(members)
        list_members = list(map(serialize_mongo_doc, list_members))
        return list_members
    elif request.method == "POST":
        new_member = {
            "name": request.form["name"],
            "dob": request.form["dob"],
            "address": request.form["address"],
            "phno": request.form["phno"],
            "email": request.form["email"],
            "type": request.form["type"],
            "joindate": request.form["joindate"],
            "expirydate": request.form["expirydate"],
        }
        other_members = mongo.db.get_collection("members").find(
            {"phno": new_member["phno"]}
        )
        if len(list(other_members)) > 0:
            return {"message": "User already exists"}

        memberdoc = mongo.db.get_collection("members").insert_one(new_member)
        return {"message": "Member inserted!", "member_id": str(memberdoc.inserted_id)}
    else:
        abort(405)


@app.route("/members/<member_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def singleMember(member_id):
    member = mongo.db.get_collection("members").find_one({"_id": ObjectId(member_id)})
    if member is None:
        return {"message": "Member not found"}, 404
    if request.method == "GET":
        return serialize_mongo_doc(member)
    elif request.method == "PUT":
        updated_member = {
            "name": request.form["name"],
            "dob": request.form["dob"],
            "address": request.form["address"],
            "phno": request.form["phno"],
            "email": request.form["email"],
            "type": request.form["type"],
            "joindate": request.form["joindate"],
            "expirydate": request.form["expirydate"],
        }
        mongo.db.get_collection("members").update_one(
            {"_id": ObjectId(member_id)}, {"$set": updated_member}
        )
        return {"message": "Updated Successfully"}
    elif request.method == "DELETE":
        mongo.db.get_collection("members").delete_one({"_id": ObjectId(member_id)})
        return {"members": "Member deleted"}
    else:
        abort(405)


@app.route("/trainers", methods=["GET", "POST"])
@jwt_required()
def trainers():
    if request.method == "GET":
        trainers = mongo.db.get_collection("trainers").find()
        list_trainers = list(trainers)
        list_trainers = list(map(serialize_mongo_doc, list_trainers))
        return list_trainers
    elif request.method == "POST":
        new_trainer = {
            "name": request.form["name"],
            "phno": request.form["phno"],
            "email": request.form["email"],
            "speciality": request.form["speciality"],
        }
        other_trainer = mongo.db.get_collection("trainers").find(
            {"phno": new_trainer["phno"]}
        )
        if len(list(other_trainer)) > 0:
            return {"message": "member already exists"}
        trainerdoc = mongo.db.get_collection("trainers").insert_one(new_trainer)
        return {"message": "Trainer added", "trainer_id": str(trainerdoc.inserted_id)}
    else:
        abort(405)


@app.route("/trainers/<trainer_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def singleTrainer(trainer_id):
    trainer = mongo.db.get_collection("trainers").find_one(
        {"_id": ObjectId(trainer_id)}
    )
    if trainer is None:
        return {"message": "Trainer not found"}, 404
    if request.method == "GET":
        return serialize_mongo_doc(trainer)
    elif request.method == "PUT":
        updated_trainer = {
            "name": request.form["name"],
            "phno": request.form["phno"],
            "email": request.form["email"],
            "speciality": request.form["speciality"],
        }
        mongo.db.get_collection("trainers").update_one(
            {"_id": ObjectId(trainer_id)}, {"$set": updated_trainer}
        )
        return {"message": "Updated Successfully"}
    elif request.method == "DELETE":
        mongo.db.get_collection("trainers").delete_one({"_id": ObjectId(trainer_id)})
        return {"message": "Trainer Deleted"}
    else:
        abort(405)


@app.route("/equipments", methods=["GET"])
@jwt_required()
def allequipments():
    equipments = mongo.db.get_collection("equipments").find()
    if equipments is None:
        return {"message": "Equipment not found"}
    if request.method == "GET":
        list_equipments = list(equipments)
        list_equipments = list(map(serialize_mongo_doc, list_equipments))
        return list_equipments
    else:
        abort(405)


@app.route("/equipments/<int:equipment_id>", methods=["GET"])
@jwt_required()
def singleequipment(equipment_id):
    equipement = mongo.db.get_collection("equipments").find_one(
        {"id": equipment_id}, {"name": equipment_id, "type": equipment_id}
    )
    if equipement is None:
        return {"message": "Equipment not found"}
    return serialize_mongo_doc(equipement)


if __name__ == "__main__":
    app.run(debug=True)
