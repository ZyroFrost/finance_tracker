# config.py dùng để chứa mọi cấu hình quan trọng của project (MongoDB URI, tên database, tên collections, các giá trị mặc định),
# giúp code gọn, dễ quản lý và tránh trùng lặp.

import os
from dotenv import load_dotenv

load_dotenv()

# MONGO configuration
MONGO_URI = os.getenv("MONGO_URI", "localhost:2017") # localhost:2017 by default (prevent errors when running on localhost)
DATABASE_NAME = "finance_tracker"

# Collections (tương đương tables trong SQL)
COLLECTIONS = {
    "user": "users",
    "transaction": "transactions",
    "category": "categories",
    "budget": "budgets"
}

# Transaction types (use for dropdown list)
TRANSACTION_TYPES = ["Expense", "Income"]

# Categories expense (use for dropdown list)
DEFAULT_CATEGORIES_EXPENSE = [
    "Shopping",
    "Transportation",
    "Entertainment",
    "Others"
]

# Categories income (use for dropdown list)
DEFAULT_CATEGORIES_INCOME = [
    "Wave",
    "Others"
]

'''
 # Check if MONGO_URI is set
if __name__ == "__main__":
    if not MONGO_URI:
        print("MONGO_URI is not set. Please set it in the .env file.")
        exit(1)

    print("CONNECT DATABASE SUCCESSFULLY! \n")
    print("Environment variables:")
    print("__MONGO_URI:", MONGO_URI)
    print("__DATABASE_NAME:", DATABASE_NAME)
    print("__COLLECTIONS:", COLLECTIONS)
    print("__TRANSACTION_TYPES:", TRANSACTION_TYPES)
    print("__DEFAULT_CATEGORIES_EXPENSE:", DEFAULT_CATEGORIES_EXPENSE)
    print("__DEFAULT_CATEGORIES_INCOME:", DEFAULT_CATEGORIES_INCOME)
#'''