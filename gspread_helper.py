from pymongo import MongoClient

# 初始化 MongoDB 客戶端
client = MongoClient("mongodb+srv://bubble60324:RainonSunny0@cluster0.xzijt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # 替換為你的 MongoDB URI
db = client["vocab_db"]  # 資料庫名稱
collection = db["users"]  # 集合名稱

# 新增使用者 ID（如果不存在）
def add_user(user_id):
    if not collection.find_one({"user_id": user_id}):
        collection.insert_one({"user_id": user_id, "vocab": []})

# 取得所有使用者 ID
def get_all_users():
    return [user["user_id"] for user in collection.find({}, {"user_id": 1})]

# 取得某個使用者的單字清單
def get_user_vocab(user_id):
    user = collection.find_one({"user_id": user_id})
    return user["vocab"] if user else []

# 為使用者加入新的單字（不重複）
def add_user_vocab(user_id, new_vocab):
    user = collection.find_one({"user_id": user_id})
    if user:
        vocab_list = user["vocab"]
        if new_vocab not in vocab_list:
            vocab_list.append(new_vocab)
            collection.update_one({"user_id": user_id}, {"$set": {"vocab": vocab_list}})
    else:
        # 若使用者尚未存在則新增
        collection.insert_one({"user_id": user_id, "vocab": [new_vocab]})
