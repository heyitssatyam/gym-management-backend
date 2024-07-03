def serialize_mongo_doc(mongo_doc):
    mongo_doc["_id"] = str(mongo_doc["_id"])
    return mongo_doc