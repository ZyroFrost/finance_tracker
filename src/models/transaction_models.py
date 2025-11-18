from core import config
from core.database_manager import DatabaseManager
from bson import ObjectId

collection_name = config.COLLECTIONS['transaction'] # Lấy collection transaction từ config

class TransactionModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(collection_name=collection_name)
         # 1 self (instance) có t hể chứa nhiều thuộc tính, ở đây là self.collection và self.db_manager
         # mỗi thuộc tính dùng được cho nhiều mục đích khác nhau

    # Hàm thêm transaction
    def add_transaction(self, transaction_data: dict):
        return self.collection.insert_one(transaction_data) # self.collection để gọi thuộc tính collection trong class (từ self)
    
    # Hàm xóa transaction theo id
    def delete_transaction(self, transaction_id: str):
        return self.collection.delete_one({"_id": ObjectId(transaction_id)})
    # _id là hệ thống của MongoDB tự tạo khi add_transaction ở trên
    # _id KHÔNG phải string, _id là kiểu: ObjectId("xxxxxxxxxx")
    # Vì MongoDB lưu _id dưới dạng ObjectId, không phải string. Nên muốn tìm đúng document, phải chuyển: về ObjectId,
    # Nếu không chuyển → MongoDB không tìm ra → update / delete thất bại
    
    # Hàm update transaction theo id
    def update_transaction(self, transaction_id: str, transaction_data: dict):
        result = self.collection.update_one(
            {"_id": ObjectId(transaction_id)}, 
            {"$set": transaction_data}) # $set là toán tử của update dữ liệu, set dữ liệu mới cần đổi
        return result  
    
    # Hàm tìm transaction theo id
    def get_transaction_by_id(self, transaction_id: str):
        result = self.collection.find_one({"_id": ObjectId(transaction_id)}) # Dùng find_one, vì id chỉ tìm đúng 1 document
        return result

    # Hàm tìm transaction theo type
    def get_transaction_by_type(self, type: str):
        result = self.collection.find({"type": type}) # dùng find vì tìm theo type sẽ có thể trả về nhiều kq
        return result
    
    # Hàm tìm transaction theo category
    def get_transactions_by_category(self, category: str):
        result = self.collection.find({"category": category}) # dùng find vì tìm theo category sẽ có thể trả về nhiều kq
        return result
    
    # Hàm tìm transaction theo date
    def get_transactions_by_date(self, date: str):
        result = self.collection.find({"date": date})
        return result

 
if __name__== "__main__":
    print("Init transaction collection")
    transaction = TransactionModel()