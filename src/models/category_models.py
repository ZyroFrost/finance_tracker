# MỤC ĐÍCH CỦA category_models.py: Xử lý toàn bộ CRUD (Create, Read, Update, Delete) cho Category
# backend cho các nút: Add Category, Get Category, Delete Category, Update Category trên App

# import sys
# from pathlib import Path

# ROOT_PATH = str(Path(__file__).resolve().parents[3])
# sys.path.insert(0, ROOT_PATH)

from core.database_manager import DatabaseManager   
from core import config
from datetime import datetime

collection_name = config.COLLECTIONS['category'] # Lay ten collection tu config

# Class xử lý CRUD cho CategoryModel
class CategoryModel:

    # Tạo instance DatabaseManager (singleton → 1 kết nối duy nhất)
    def __init__(self):
        self.db_manager = DatabaseManager() # tạo instance DatabaseManager (instance = 1 đối tượng của Class)
        self.collection = self.db_manager.get_collection(collection_name=collection_name) # lấy collection từ DatabaseManager

    # Khoi tao category mac dinh
    def __initialize_default_categories__(self):

        # EXPENSE
        for cate in config.DEFAULT_CATEGORIES_EXPENSE: # Lặp từng Key trong Expense (Shopping, Transportation, ...)
        # Mỗi 1 Key (Shopping, Transportation, ...) tạo 1 item với cấu trúc phía dưới, gọi là document (tuong đương row trong SQL)
            item = { 
                "type": "Expense",
                "name": cate,
                "created_at": datetime.now(),
                "last_modified": datetime.now() 
            }
            self.collection.update_one( # code này để update nếu có rồi, nếu tìm thấy → Mongo không chèn mới, chỉ bỏ qua
                {"name": cate, "type": "Expense"},
                {"$setOnInsert": item}, # → Nhờ "$setOnInsert" nên update cũng không ghi đè => Không bị trùng category.
                upsert=True #
            )
        # Hàm này chủ yếu tạo header row cho từng category của EXPENSE (Shopping, Transportation, ...)

        ''' # Giải thích cách hoạt động của update_one
            update_one(filter, update) → Nếu tìm thấy document → UPDATE / Nếu không thấy → KHÔNG LÀM GÌ (KHÔNG INSERT)
            update_one(filter, update, upsert=True) → Nếu tìm được document → UPDATE Nếu KHÔNG tìm được → TẠO Document MỚI
            (Upsert = update + insert)
        '''

        ''' # Giải thích $setOnInsert
            $setOnInsert = chỉ chạy khi INSERT xảy ra → Còn nếu là UPDATE thì không chạy.
            Nếu document đã tồn tại → Upsert chọn UPDATE → $setOnInsert KHÔNG chạy → Không ghi đè dữ liệu cũ → Không tạo mới
            Nếu document không tồn tại → Upsert chọn INSERT → $setOnInsert: item sẽ tạo document mới với item
        '''

        ''' # Giải thích tại sao phải có upsert=True + $setOnInsert cùng lúc
            Nếu thiếu upsert=True, thì sẽ không có insert 
                → $setOnInsert KHÔNG BAO GIỜ chạy, vì phải có insert mới chạy dc
                → Dữ liệu MẶC ĐỊNH không bao giờ được chèn vào DB.

            # Hai cái này phải đi chung:
                upsert=True → Cho phép insert nếu cần
                $setOnInsert → Gán giá trị chỉ khi insert
        '''

        # INCOME
        for cate in config.DEFAULT_CATEGORIES_INCOME:
            item = { 
                "type": "Income",
                "name": cate,
                "created_at": datetime.now(),
                "last_modified": datetime.now() 
            }
            self.collection.update_one(
                {"name": cate, "type": "Income"},
                {"$setOnInsert": item},
                upsert=True
            )

    # Nút thêm category
    def add_category(self, type: str, category_name: str):

        # tạo dict item bằng cấu trúc phía dưới, đây là cấu trúc document phải theo mẫu __initialize_default_categories__ ở trên
        # mục đích tạo dict để dễ check tồn tại chưa, 
        # nhưng chỉ add trước 2 cột giá trị type, name, còn 2 cột time thì xử lý phía dưới
        item_add = {
            "type": type,
            "name": category_name,
        } 

        # Kiểm tra category name có tồn tại ko
        item_existing = self.collection.find_one({"type": type, "name": category_name})

        if item_existing: # Nếu tìm thấy category name (có tồn tại)
            item_add['last_modified'] = datetime.now() # thêm cót giá trị last_modified (vì đã có cột created_at rồi)
        else: # Nếu không tìm thấy category name (chưa tạo)
            item_add['created_at'] = datetime.now() # thêm cột giá trị created_at
            item_add['last_modified'] = datetime.now() # thêm cót giá trị last_modified

        self.collection.update_one( # code này giống ở trên, tìm thấy thì chỉ update, không thì insert
            {"name": category_name, "type": type},
            {"$setOnInsert": item_add},
            upsert=True
        )

    # Nút xóa category
    def delete_category(self, type: str, category_name: str):
        result = self.collection.delete_one({"name": category_name, "type": type}) 
        return result

    # Nút tim kiếm category theo type
    def get_category_by_test(self, type: str):
        result = self.collection.find({"type": type})
        return result

#'''
if __name__== "__main__":
    print("Init category collection")
    cate = CategoryModel() 
    # gán cate chỉ dùng khi test file 1 mình, cate là 1 object (instance) của class CategoryModel, để xem class có lỗi hay không
    # gán cate để dễ debug (có thể mở Python REPL hay debug và kiểm tra) -> ví dụ lấy cate print(cate.collection) để kiểm tra
#'''