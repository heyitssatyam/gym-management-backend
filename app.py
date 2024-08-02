import requests
from flask import Flask, request, abort, render_template, session, redirect, flash

from flask_session import Session
from flask_pymongo import PyMongo
from secrets_1 import MONGODB_URI
from hashlib import sha256

from helpers import serialize_mongo_doc
from bson.objectid import ObjectId
from flask_cors import CORS
from functools import wraps

UPLOAD_FOLDER = "./static"
ALLOWED_EXTENTIONS = {"png", "jpeg", "jpg", "webp"}
app = Flask(__name__, static_folder="./static")
CORS(app, supports_credentials=True)

app.config["MONGO_URI"] = MONGODB_URI
app.config["SESSION_PERMANANT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


mongo = PyMongo(app)
Session(app)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENTIONS


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
    email = request.form["email"]
    password = request.form["password"]
    password_hash = sha256(password.encode("utf-8")).hexdigest()
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
            "trainer": None,
            "classes": None,
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


@app.route("/dashboard/members/<member_id>", methods=["GET", "DELETE"])
@login_required
def singleMember(member_id):
    member = mongo.db.get_collection("members").find_one({"_id": ObjectId(member_id)})
    if member["trainer"] == None:
        trainer = None
    else:
        trainer = mongo.db.get_collection("trainers").find_one(
            {"_id": ObjectId(member["trainer"])}
        )
    if member["classes"] == None:
        classes = None
    else:
        classes = mongo.db.get_collection("classes").find_one(
            {"_id": ObjectId(member["classes"])}
        )
    if member is None:
        return {"message": "Member not found"}, 404
    if request.method == "GET":
        return render_template(
            "viewmember.html", member=member, trainer=trainer, classes=classes
        )
    else:
        abort(405)


@app.route(
    "/dashboard/members/<member_id>/add-trainer-to-member", methods=["GET", "POST"]
)
@login_required
def addTrainerToMember(member_id):
    member = mongo.db.get_collection("members").find_one({"_id": ObjectId(member_id)})
    trainers = mongo.db.get_collection("trainers").find()
    list_trainers = list(trainers)
    list_trainers = list(map(serialize_mongo_doc, list_trainers))
    if request.method == "GET":
        return render_template(
            "addTrainerToMember.html", trainers=list_trainers, member=member
        )
    if request.method == "POST":
        trainer_id = request.form.get("trainer")
        doc = mongo.db.get_collection("members").update_one(
            {"_id": ObjectId(member_id)}, {"$set": {"trainer": ObjectId(trainer_id)}}
        )
        flash("Trainer seleted succesfully")
        return redirect(f"/dashboard/members/{member_id}")
    return redirect("/dashboard/members")


@app.route(
    "/dashboard/members/<member_id>/add-class-to-member", methods=["GET", "POST"]
)
@login_required
def addClassToMember(member_id):
    member = mongo.db.get_collection("members").find_one({"_id": ObjectId(member_id)})
    classes = mongo.db.get_collection("classes").find()
    list_classes = list(classes)
    list_classes = list(map(serialize_mongo_doc, list_classes))
    if request.method == "GET":
        return render_template(
            "addClassToMember.html", member=member, classes=list_classes
        )
    if request.method == "POST":
        class_id = request.form.get("classes")
        doc = mongo.db.get_collection("members").update_one(
            {"_id": ObjectId(member_id)}, {"$set": {"classes": ObjectId(class_id)}}
        )
        flash("Class added successfully")
        return redirect(f"/dashboard/members/{member_id}")
    else:
        abort(405)


@app.route("/dashboard/members/<member_id>/delete")
@login_required
def deletemember(member_id):
    member = mongo.db.get_collection("members").find_one({"_id": ObjectId(member_id)})
    mongo.db.get_collection("removed").insert_one(member)
    mongo.db.get_collection("members").delete_one(member)

    flash("Member deleted")
    return redirect("/dashboard/members")


@app.route("/dashboard/trainers", methods=["GET", "POST"])
@login_required
def trainers():
    if request.method == "GET":
        trainers = mongo.db.get_collection("trainers").find()
        list_trainers = list(trainers)
        list_trainers = list(map(serialize_mongo_doc, list_trainers))
        return render_template("viewtrainers.html", trainers=list_trainers)
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
        return render_template("viewtrainer.html", trainer=trainer)
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


@app.route("/dashboard/trainers/<trainer_id>/delete")
@login_required
def deletetrainer(trainer_id):
    trainer = mongo.db.get_collection("trainers").find_one(
        {"_id": ObjectId(trainer_id)}
    )
    mongo.db.get_collection("removed").insert_one(trainer)
    mongo.db.get_collection("trainers").delete_one(trainer)
    flash("Trainer deleted")
    return redirect("/dashboard/trainers")


def addTrainer(classInfo):
    trainer = mongo.db.get_collection("trainers").find_one(
        {"_id": classInfo["trainer_id"]}
    )
    if trainer is None:
        classInfo["trainer"] = "Trainer not found"
        return classInfo
    classInfo["trainer"] = trainer["name"]
    return classInfo


def addMember(classInfo):
    member = mongo.db.get_collection("members").find_one(
        {"_id": classInfo["member_id"]}
    )
    if member is None:
        classInfo["member"] = "Member not found"
        return classInfo
    classInfo["member"] = member["name"]
    return classInfo


@app.route("/dashboard/classes", methods=["GET", "POST"])
def classes():
    classes = mongo.db.get_collection("classes").find()
    trainers = mongo.db.trainers.find()
    list_trainers = list(
        map(serialize_mongo_doc, list(trainers))
    )  # i think it is of no use
    if request.method == "GET":

        list_classes = list(classes)
        list_classes = list(map(serialize_mongo_doc, list_classes))
        # for classes in list_classes:
        #     if classes["trainer_id"]:
        #         mongo.db.get_collection("classes").delete_one(classes)
        #         return redirect("/dashboard/classes")
        list_classes = list(map(addTrainer, list_classes))
        return render_template("viewclasses.html", classes=list_classes)
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


@app.route("/dashboard/classes/<class_id>", methods=["GET"])
def viewclass(class_id):
    classes = mongo.db.get_collection("classes").find_one({"_id": ObjectId(class_id)})
    classes = addTrainer(classes)
    return render_template("viewclass.html", classes=classes)


@app.route("/dashboard/classes/<class_id>/delete")
def removeclasses(class_id):
    classes = mongo.db.get_collection("classes").find_one({"_id": ObjectId(class_id)})
    mongo.db.get_collection("removed").insert_one(classes)
    mongo.db.get_collection("classes").delete_one(classes)
    flash("Class deleted")
    return redirect("/dashboard/classes")


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


@app.route("/dashboard/equipments/add", methods=["GET", "POST"])
@login_required
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            payload = {
                "type": "image",
                "title": f"{request.form.get('name')}-GYM-EQUIPMENT",
            }
            files = [("image", (file.filename, file.stream, file.mimetype))]
            headers = {"Authorization": "Client-ID 09ebcd2cb3c4cfc"}
            url = "https://api.imgur.com/3/image"
            resp = requests.post(url, headers=headers, data=payload, files=files)
            if not resp.ok:
                flash("Unable to upload image. Please try again later.")
                return redirect("/dashboard/equipments/add")
            doc = {
                "name": request.form.get("name"),
                "type": request.form.get("type"),
                "url": resp.json()["data"]["link"],
            }
            mongo.db.equipments.insert_one(doc)
            return redirect("/dashboard/equipments")
    return render_template("addequipment.html")


@app.route("/dashboard/equipments/<equipment_id>/remove")
def remove_equipment(equipment_id):
    mongo.db.get_collection("equipments").delete_one({"_id": ObjectId(equipment_id)})
    return redirect("/dashboard/equipments")


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


@app.route("/dashboard/payments", methods=["GET", "POST"])
@login_required
def payments():
    payments = mongo.db.get_collection("payment").find()
    if payments is None:
        flash("NO payment history")
        return redirect("/dashboard/payments/add")
    elif request.method == "GET":
        list_payments = list(payments)
        list_payments = list(map(serialize_mongo_doc, list_payments))
        list_payments = list(map(addMember, list_payments))
        return render_template("payments.html", payments=list_payments)
    elif request.method == "POST":
        member_id = request.form.get("member_id")
        amount = request.form.get("amount")
        paydate = request.form.get("paydate")
        paymethod = request.form.get("paymethod")

        new_payment = {
            "member_id": ObjectId(member_id),
            "amount": amount,
            "paydate": paydate,
            "paymethod": paymethod,
        }
        paydoc = mongo.db.get_collection("payment").insert_one(new_payment)
        flash("Payment added")
        return redirect("/dashboard/payments")
    else:
        abort(405)


@app.route("/dashboard/payments/add")
@login_required
def addpayments():
    members = mongo.db.members.find()
    members = list(map(serialize_mongo_doc, list(members)))
    return render_template("addpayment.html", members=members)


if __name__ == "__main__":
    app.run(debug=True)
