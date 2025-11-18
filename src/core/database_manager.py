# Mục đích chính của database_manager.py,
# Để toàn bộ project dùng chung 1 kết nối chuẩn.
# Thay vì mỗi file phải tự viết:
    # client = MongoClient(MONGO_URI)
    # db = client[DATABASE_NAME]
# → Tạo một file quản lý sự kết nối là đúng chuẩn backend.
# Đây là chuẩn Singleton pattern

from pymongo import MongoClient # để tạo kết nối DB
from core import config

class DatabaseManager: 
    _instance = None # là biến chứa đối tượng (object) duy nhất của class này → Cả project chỉ tạo 1 kết nối DB, không tạo nhiều lần.
    # các file .py khác sẽ dùng chung 1 _instance của class này
    # dấu _ (gạch dưới đầu) = biến nội bộ / private / không dùng bên ngoài (cách đặt tên chuẩn)

    # Tránh tạo nhiều connections đến MongoDB.
    def __new__(cls): # cls = class 
        if cls._instance is None: # nếu _instance chua duoc khoi tao
            cls._instance = super(DatabaseManager, cls).__new__(cls) # tạo 1 instance
            cls._instance._initialize() # thực hành phương thức khởi tạo (gọi def phía dưới)
        return cls._instance # trả về instance
    # Lần đầu gọi DatabaseManager(): _instance là None → tạo object mới → chạy _initialize()
    # Những lần sau: _instance đã tồn tại → trả về object cũ
    # → Không bao giờ tạo kết nối MongoDB thêm lần nữa.

    # Hàm _initialize() – Khởi tạo kết nối DB, khởi tạo khi chạy hàm new ở trên
    def _initialize(self):
        self.client = MongoClient(config.MONGO_URI) # tạo kết nối DB bằng hàm MongoClient, lấy thông tin server DB từ config.py
        self.db = self.client[config.DATABASE_NAME] # tạo database bằng hàm client[ten database], lấy tên từ config.py
        try:
            self.db.command("ping") # Gửi command Ping tới DB để kiểm tra có kết nối chưa
            print("Initialize DB successfully!") # In ra khi kết nối DB thành công
        except Exception as e:
            print(f"Error in connect: {e}")
            raise e

    # Hàm get_collection()
    def get_collection(self, collection_name: str):
        return self.db[collection_name] #Get a collection from DB

    # Hàm close_connection()
    def close_connection(self):
        if self.client: # Kiểm tra co kết nối DB chưa
            self.client.close()
            print("Shutdown DB connection")
        else:
            print("There is no DB connecting!")

''' # Kiểm tra class có chạy ko
if __name__== "__main__":
    # Test 3 loại:

    # 1. Test kết nối DB
    test_db = DatabaseManager()
    # tạo / lấy instance của DatabaseManager để quản lý kết nối MongoDB.
    # Instance = một đối tượng (object) được tạo ra từ một class.
    # gán biến test_db để tự chạy class
    

    # 2. Test lấy collection
    # Trong Class DatabaseManager() tạo biến collection_name (tham số cần trong hàm get_collection)
    collection_name = "users" # Lấy collection Users (tương đương table trong SQL), để đưa xuống biến ở dưới
    user_collection = test_db.get_collection(collection_name=collection_name) 
    # Thêm 1 biến chứa chính xác collection users bằng hàm get_collection, truyền tham số collection_name
    # (tham số cần trong hàm get_collection)
    if user_collection is not None:
        print("Get collection successfully!")


    # 3. Test đóng kết nối DB
    test_db.close_connection() # chạy xong thì đóng kết nối DB
#'''