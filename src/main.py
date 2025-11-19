from core.database_manager import DatabaseManager
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel 

if __name__ == "__main__":

    print("\n===== TEST DATABASE =====")
    DB = DatabaseManager()

    print("\n===== TEST CRUD =====")
    print("== TEST CATEGORY MODEL ==")
    cate = CategoryModel()
    cate.add_category(type="expense", category_name="clothing")    
    print("Category added successfully!")

    print("\n== TEST TRANSACTION MODEL ==")
    tran = TransactionModel()
    tran.add_transaction({"type": "expense", "category": "clothing", "amount": 1000})
    print("Transaction added successfully!")