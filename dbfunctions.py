from bson import ObjectId
from datetime import datetime

def init_db(db):
    # MongoDB creates collections automatically when we insert documents
    # So we don't need to explicitly create tables/collections
    pass

def add_user(db, username):
    users = db.users
    user = users.find_one({"username": username})
    if not user:
        users.insert_one({"username": username})
        db.user_profiles.insert_one({"username": username})

def get_user(db, username):
    return db.users.find_one({"username": username})

def get_all_users(db, current_username):
    return list(db.users.find({"username": {"$ne": current_username}}))

def get_chatted_users(db, username):
    messages = db.messages
    chatted_users = messages.aggregate([
        {"$match": {"$or": [{"user1": username}, {"user2": username}]}},
        {"$project": {
            "other_user": {
                "$cond": [
                    {"$eq": ["$user1", username]},
                    "$user2",
                    "$user1"
                ]
            }
        }},
        {"$group": {"_id": "$other_user"}},
        {"$project": {"username": "$_id", "_id": 0}}
    ])
    return list(chatted_users)

def save_message(db, user1, user2, message):
    messages = db.messages
    result = messages.insert_one({
        "user1": user1,
        "user2": user2,
        "message": message,
        "timestamp": datetime.utcnow()
    })
    return str(result.inserted_id)

def get_user_profile(db, username):
    return db.user_profiles.find_one({"username": username})

def update_user_profile(db, username, avatar, status_message):
    db.user_profiles.update_one(
        {"username": username},
        {"$set": {"avatar": avatar, "status_message": status_message}}
    )

def mark_message_as_read(db, message_id, reader):
    db.read_receipts.insert_one({
        "message_id": ObjectId(message_id),
        "reader": reader,
        "read_at": datetime.utcnow()
    })

def get_unread_messages(db, username, partner):
    messages = db.messages.aggregate([
        {"$match": {
            "$or": [
                {"user1": username, "user2": partner},
                {"user1": partner, "user2": username}
            ]
        }},
        {"$lookup": {
            "from": "read_receipts",
            "localField": "_id",
            "foreignField": "message_id",
            "as": "receipts"
        }},
        {"$match": {
            "receipts": {"$size": 0}
        }},
        {"$sort": {"timestamp": 1}}
    ])
    return list(messages)

def get_messages(db, user1, user2):
    return list(db.messages.find({
        "$or": [
            {"user1": user1, "user2": user2},
            {"user1": user2, "user2": user1}
        ]
    }).sort("timestamp", 1))