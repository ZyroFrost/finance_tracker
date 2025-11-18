from core.database_manager import DatabaseManager
from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel 

if __name__ == "__main__":

    print("===== TEST DATABASE =====")
    DB = DatabaseManager()

    print("===== TEST CONFIG =====")
    test = config.COLLECTIONS['category']

    print("===== TEST CATEGORY MODEL =====")
    cate = CategoryModel()

    print("===== TEST TRANSACTION MODEL =====")
    tran = TransactionModel()