# MỤC ĐÍCH CỦA category_models.py: Xử lý toàn bộ CRUD (Create, Read, Update, Delete) cho Category
# backend cho các nút: Add Category, Get Category, Delete Category, Update Category trên App
from core.database_manager import DatabaseManager
from core import config
from bson import ObjectId
from typing import Optional # hàm Optional để khai báo biến có thể là None hoặc kiểu khác
from datetime import datetime

# Class xử lý CRUD cho CategoryModel
class CategoryModel:

    # Tạo instance DatabaseManager (singleton → 1 kết nối duy nhất)
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(config.COLLECTIONS['category']) # lấy collection từ DatabaseManager
        self.user_id = user_id # lấy tham số user_id từ google auth truyền vào

    def set_user_id(self, user_id: str): # → Dùng sau khi user đăng nhập, để cập nhật user_id
        self.user_id = ObjectId(user_id) if user_id is not None else None

    # Khoi tao category mac dinh
    def __initialize_default_categories__(self):

        # Check if there is user_id, exist earlier
        if not self.user_id:
            return
        
        # EXPENSE
        for cate in config.DEFAULT_CATEGORIES_EXPENSE: # Lặp từng Key trong Expense (Shopping, Transportation, ...)
            self.save_category(category_type = "Expense", category_name= cate, icon=config.DEFAULT_CATEGORY_ICONS.get(cate, "📁"))
                # “Nếu category có icon được định nghĩa trong config → dùng icon đó
                # Nếu chưa khai báo → dùng tạm một icon an toàn để không crash UI”
                # 📁 = icon trung tính, không mang nghĩa tài chính cụ thể

        # INCOME
        for cate in config.DEFAULT_CATEGORIES_INCOME:
            self.save_category(category_type = "Income", category_name= cate, icon=config.DEFAULT_CATEGORY_ICONS.get(cate, "📁"))

    # Save category, ko dùng upsert filter_, vì hàm này tích hợp luôn create và update fields name và type
    def save_category(self, category_id: str | None, category_type: str, category_name: str, icon: str = ""):
        """
        Save category (create or update).
        - if category_id == None -> CREATE
        - if category_id != None -> UPDATE
        """

        # validation duplicate
        query = {
            "user_id": self.user_id,
            "type": category_type,
            "name": category_name
        }

        # when update, avoid itself
        if category_id:
            query["_id"] = {"$ne": ObjectId(category_id)} # $ne = not equal, bỏ qua chính category đang sửa (editing) khi kiểm tra trùng.

        # find category in DB by query, if exists return False
        exists = self.collection.find_one(query)
        if exists:
            print("Category already exists")
            return False

        # update mode
        if category_id:
            result = self.collection.update_one(
                {"_id": ObjectId(category_id), "user_id": self.user_id},
                {
                    "$set": {
                        "type": category_type,
                        "name": category_name,
                        "icon": icon,
                        "last_modified": datetime.now()
                    }
                }
            )
            print("Updated category successfully with ID: ", category_id)
            print(result)
            return True

        # create mode
        doc = {
            "type": category_type,
            "name": category_name,
            "icon": icon,
            "user_id": self.user_id,
            "created_at": datetime.now(),
            "last_modified": datetime.now()
        }

        result = self.collection.insert_one(doc)      
        print(f"Created category successfully with ID: {str(result.inserted_id)}, name: {category_name}")
        print(doc)
        return True

    # Hàm xóa category
    def delete_category(self, category_type: str, category_name: str):
        result = self.collection.delete_one({"type": category_type, "name": category_name, "user_id": self.user_id}) # add user_id condition
        return result.deleted_count  # trả về số document đã xóa (0 hoặc 1) để check nút xóa có thành công không

    # Hàm cập nhập category
    # def update_category(self, category_id: str, category_data: dict):
    #     result = self.collection.update_one(
    #         {"_id": ObjectId(category_id), "user_id": self.user_id}, # cập nhập thêm điều kiện user_id để tránh người dùng khác cập nhập category của người khác
    #         {"$set": category_data}) # $set là toán tử của update dữ liệu, set dữ liệu mới cần đổi
    #     return result.modified_count > 0 # trả về true false cập nhập (0 hoặc 1), nếu 1 là thành công thì mới return dữ liệu

    def get_categories(self):
        if not self.user_id:
            return []
        return list(self.collection.find({"user_id": self.user_id}).sort("created_at", -1))

    # Hàm tìm category theo type, có thể tìm All
    def get_category_by_type(self, category_type: str) -> list:
        query = {"user_id": self.user_id} # tạo query chung cho 2 trường hợp (All và Expense/Income)
        if category_type in ["Expense", "Income"]: # nếu truyền vào Expense hoặc Income, tìm theo type
            query["type"] = category_type # nếu có type thì thêm điều kiện type vào query
        return list(self.collection.find(query).sort("created_at", -1))  # -1 = giảm dần (descending)
    
    # Hàm lấy tên category từ ID (dùng cho transaction vì transaction chỉ lưu category_id)
    def get_category_name_by_id(self, category_id: ObjectId) -> str:
        doc = self.collection.find_one({
            "_id": ObjectId(category_id),
            "user_id": self.user_id
        })
        return doc["name"] if doc else None # Kiểm tra None trong trường hợp đặc biệt nếu user xóa category rồi mà transaction vẫn còn tham chiếu đến category đó, 
        # hoặc user đổi tài khoản vẫn lưu category_id cũ từ user khác

    # This function returns the category ID based on the category name, trasfer category name to id before saving to a new transaction
    def get_category_id_by_name(self, category_name: str) -> ObjectId:
        doc = self.collection.find_one({
            "name": category_name,
            "user_id": self.user_id
        })
        return doc["_id"] if doc else None

    # This function returns a dictionary where the keys are the category names and the values are the category IDs, use to put in selectbox
    def get_category_name_by_type(self, category_type: str) -> dict:
        categories = self.get_category_by_type(category_type)
        return {c["name"]: str(c["_id"]) for c in categories}
    
    def get_category_by_id(self, category_id: ObjectId) -> dict | None:
        return self.collection.find_one({
            "_id": ObjectId(category_id),
            "user_id": self.user_id
        })
    
    def count_category_by_user(self, user_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": ObjectId(user_id)})
    
'''
if __name__== "__main__":
    print("Init category collection")
    cate = CategoryModel() 
    #cate.get_category_by_type(type="Income")
    #cate.get_category_name_by_id("69226b9f5bc8d2cb663e25bc") # test get name
    # gán cate chỉ dùng khi test file 1 mình, cate là 1 object (instance) của class CategoryModel, để xem class có lỗi hay không
    # gán cate để dễ debug (có thể mở Python REPL hay debug và kiểm tra) -> ví dụ lấy cate print(cate.collection) để kiểm tra
    # print(cate.get_category_by_type("All")[0]["name"], "\n")
    print(cate.count_category_by_user("692dd7d3f9d1d3f57cd055aa"))
#'''