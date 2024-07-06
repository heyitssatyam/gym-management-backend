from flask import (
    Flask,
    request,
    jsonify,
    abort,
    render_template,
    session,
    redirect,
    flash,
)
from flask_session import Session
from flask_pymongo import PyMongo
from secrets_1 import MONGODB_URI, JWT_SECRET_KEY
from hashlib import sha256

from helpers import serialize_mongo_doc
from bson.objectid import ObjectId
from datetime import timedelta, datetime
from flask_cors import CORS
from functools import wraps


app = Flask(__name__, static_folder="./static")
CORS(app, supports_credentials=True)

app.config["MONGO_URI"] = MONGODB_URI
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["SESSION_PERMANANT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

mongo = PyMongo(app)
Session(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "_id" not in session:
            flash("Login Required")
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def home():
    return render_template("index.html", name="home")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name="dashboard")


@app.route("/about")
def about():
    return render_template("about.html", name="about")


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
        session["username"] = doc["username"]
        session["_id"] = str(doc["_id"])
        return redirect("/dashboard")
    else:
        flash("Invalid Username / Password")
        return redirect("/")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard/members", methods=["GET", "POST"])
@login_required
def members():
    if request.method == "GET":
        members = mongo.db.get_collection("members").find()
        list_members = list(members)
        list_members = list(map(serialize_mongo_doc, list_members))
        return render_template("viewmembers.html", members=list_members)
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
            flash("User already exists")
            return redirect("/dashboard/members")

        memberdoc = mongo.db.get_collection("members").insert_one(new_member)
        flash("Members Inserted")
        return redirect("/dashboard/members")
    else:
        abort(405)


@app.route("/dashboard/members/add")
@login_required
def addmembers():
    return render_template("addmembers.html")


@app.route("/dashboard/members/<member_id>", methods=["GET", "PUT", "DELETE"])
@login_required
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


@app.route("/dashboard/trainers", methods=["GET", "POST"])
@login_required
def trainers():
    if request.method == "GET":
        trainers = mongo.db.get_collection("trainers").find()
        list_trainers = list(trainers)
        list_trainers = list(map(serialize_mongo_doc, list_trainers))
        return render_template("viewtrainer.html", trainers=list_trainers)
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
            flash("Trainer already exists")
            return redirect("/dashboard/trainers")
        trainerdoc = mongo.db.get_collection("trainers").insert_one(new_trainer)
        flash("Trainer inserted")
        return redirect("/dashboard/trainers")
    else:
        abort(405)


@app.route("/dashboard/trainers/add")
@login_required
def addtrainers():
    return render_template("addtrainers.html")


@app.route("/dashboard/trainers/<trainer_id>", methods=["GET", "PUT", "DELETE"])
@login_required
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


@app.route("/dashboard/classes", methods=["GET", "POST"])
def classes():
    classes = mongo.db.get_collection("classes").find()
    trainers = mongo.db.trainers.find()
    list_trainers = list(map(serialize_mongo_doc, list(trainers)))
    if request.method == "GET":
        list_classes = list(classes)
        list_classes = list(map(serialize_mongo_doc, list_classes))
        return render_template(
            "viewclasses.html", classes=list_classes, trainers=list_trainers
        )
    elif request.method == "POST":
        name = request.form.get("name")
        schedule = request.form.get("schedule")
        duration = request.form.get("duration")
        trainer_id = request.form.get("trainer_id")
        new_class = {
            "name": name,
            "schedule": schedule,  # schedule is None in db
            "duration": duration,
            "trainer_id": ObjectId(trainer_id),
        }
        classesdoc = mongo.db.get_collection("classes").insert_one(new_class)
        flash("Classes inserted")
        return redirect("/dashboard/classes")
    else:
        abort(405)


@app.route("/dashboard/classes/add")
def addclasses():
    trainers = mongo.db.trainers.find()
    list_trainers = list(map(serialize_mongo_doc, list(trainers)))
    return render_template("addclass.html", trainers=list_trainers)

@app.route("/dashboard/equipments", methods=["GET"])
@login_required
def allequipments():
    equipments = mongo.db.get_collection("equipments").find()
    if equipments is None:
        flash("Equipment not found")
        return redirect("/dashboard/equipments")

    if request.method == "GET":
        list_equipments = list(equipments)
        list_equipments = list(map(serialize_mongo_doc, list_equipments))
        return render_template("equipments.html", equipments=list_equipments)
    else:
        abort(405)


@app.route("/dashboard/equipments/<int:equipment_id>", methods=["GET"])
@login_required
def singleequipment(equipment_id):
    equipement = mongo.db.get_collection("equipments").find_one(
        {"id": equipment_id}, {"name": equipment_id, "type": equipment_id}
    )
    if equipement is None:
        flash("Equipment Not found")
        return redirect("/dashboard/equipments")
    return serialize_mongo_doc(equipement)


if __name__ == "__main__":
    app.run(debug=True)
