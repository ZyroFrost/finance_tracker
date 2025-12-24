from core.database_manager import DatabaseManager
from models.category_model import CategoryModel
from core import config
from bson import ObjectId
from datetime import datetime

# Class xử lý CRUD cho UserModel
class UserModel:
    def __init__(self):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(collection_name=config.COLLECTIONS['user']) # lấy collection từ DatabaseManager

    # Hàm thêm user
    def create_user(self, email: str):
        # define user document
        user = {
            "email": email,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "display_currency": "USD",
            "is_activate": True
        }

        result = self.collection.insert_one(user)
        print("Created user successfully with:")
        print(user)

        # create default categories
        category_model = CategoryModel()
        category_model.set_user_id(str(result.inserted_id)) # convert to ObjectId properly
        category_model.__initialize_default_categories__()
        print("Created default categories successfully")

        return str(result.inserted_id)  # inserted_id là thuộc tính (attribute) của object, thêm id tự động cho user

    def login(self, email: str) -> str:
        # check user exist (use find_one)
        user = self.collection.find_one({'email': email})
        
        # case 1: user not exist:
        # create: call create_user(email)
        if not user:
            return self.create_user(email)

        # case 2: user exist but deactivate (user deleted account or locked account)
        # raise Error
        if user.get("is_activate") is not True:
            return {"status": "DEACTIVATED", "data": user}

        # all checking passed
        return str(user.get("_id"))

    def deactivate(self, user_id: str) -> bool:
        # find and update:
        user = self.collection.find_one({
            "_id": ObjectId(user_id),
            "is_activate": True
        })

        # case: not exist user
        if not user:
            raise ValueError("User not found")
        
        # user is validate and ready to deactivate -> update them
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_activate": False}}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id: ObjectId) -> bool:
        self.delete_user_with_data(user_id)
        self.collection.delete_one({'_id': ObjectId(user_id)})
        return True
    
    def delete_user_with_data(self, user_id: ObjectId) -> bool:
        uid = ObjectId(user_id)
        self.db_manager.get_collection(config.COLLECTIONS["transaction"]).delete_many({'user_id': uid})
        self.db_manager.get_collection(config.COLLECTIONS["category"]).delete_many({'user_id': uid})
        self.db_manager.get_collection(config.COLLECTIONS["budget"]).delete_many({'user_id': uid})
        self.db_manager.get_collection(config.COLLECTIONS["goal"]).delete_many({'user_id': uid})
        return True
        
    def get_user_by_email(self, email: str) -> dict:
        user = self.collection.find_one({'email': email})
        return user
    
    def get_default_currency(self, user_id: ObjectId) -> str:
        user = self.collection.find_one({'_id': user_id})
        return user.get("display_currency")
    
    def update_display_currency(self, user_id: ObjectId, currency: str) -> bool:
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        result = self.collection.update_one(
            {"_id": user_id}, 
            {"$set": {"display_currency": currency}})
        return result.modified_count > 0