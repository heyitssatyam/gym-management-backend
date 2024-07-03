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
from datetime import timedelta


app = Flask(__name__)
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
    email = request.form["email"]
    password = request.form["password"]
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    print(password_hash)
    doc = mongo.db.get_collection("users").find_one(
        {"email": email, "password": password_hash}
    )
    if doc is not None:
        access_key = create_access_token(identity=doc["username"])
        return {"message": "Successful login", "access_token": access_key}
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


if __name__ == "__main__":
    app.run(debug=True)
