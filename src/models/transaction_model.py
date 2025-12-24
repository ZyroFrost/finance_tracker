from core import config
from core.database_manager import DatabaseManager
from models.exchange_rate_model import ExchangeRateModel
from models.user_model import UserModel
from bson import ObjectId
from typing import Optional, Any
from datetime import datetime, date
from utils import handler_datetime # hàm xử lý datetime

class TransactionModel:
    
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(config.COLLECTIONS['transaction'])
        self.user_id = user_id

    def set_user_id(self, user_id: Optional[str]):
        """Set or clear the current user id used to scope queries."""
        self.user_id = ObjectId(user_id) if user_id is not None else None

    # Hàm lấy transaction với bộ lọc nâng cao
    def get_transactions(self, page=1, page_size=20, advanced_filters: dict[str, any] = None) -> list[dict]:

        # Build query filter
        query = self._build_query(advanced_filters)
        skip = (page - 1) * page_size # Tính số document cần bỏ qua (skip) để phân trang, ví dụ chọn page 1 sẽ skip 0 document, page 2 skip 20 document
        # Page	Skip	        Lấy từ dòng
        # 1	    (1−1)×20 = 0	từ dòng 1
        # 2	    (2−1)×20 = 20	từ dòng 21
        # 3	    (3−1)×20 = 40	từ dòng 41
        # 4	    (4−1)×20 = 60	từ dòng 61

        #print("TransactionModel.get_transactions - query:", query)
              
        # Fetch transactions, sort from newest to oldest
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        # -1 = descending order
        return list(cursor)  
    
    # Hàm xây dựng query từ bộ lọc nâng cao
    def _build_query(self, advanced_filter: Optional[dict]) -> dict:
        conditions = [] # list để chứa các điều kiện lọc
        if not advanced_filter: # Nếu không có advanced_filter → chỉ cần lọc theo user_id (Không có filter nào từ UI → chỉ gắn user_id rồi trả về)
            return self._add_user_constraint(conditions)
        
        # Check transaction_type_id: → Nếu UI chọn category_name → thêm điều kiện category_id, vì cấu trúc lưu trans là lưu ID ko lưu name
        t_category_id = advanced_filter.get("category_id")
        if t_category_id:
            conditions.append({"category_id": ObjectId(t_category_id)})

        # Check transaction_type: → Nếu UI chọn Income/Expense → thêm điều kiện type
        t_type = advanced_filter.get("type")
        if t_type and t_type != "All": # Nếu khác All mới thêm điều kiện lọc, trong UI thêm chọn All
            conditions.append({"type": t_type})

        # Check Category: → Lọc theo category name hoặc id (tùy user lưu gì)
        category = advanced_filter.get("category")
        if category and category != "All":
            conditions.append({"category": category})

        # Check amount:
        min_amount = advanced_filter.get("min_amount")
        max_amount = advanced_filter.get("max_amount")
        if min_amount or max_amount: # Nếu có nhập min hoặc max amount (ko thì code này skip)
            amount = {}
            if min_amount is not None:
                amount["$gte"] = min_amount # $gte = greater than or equal
            if max_amount is not None:
                amount["$lte"] = max_amount # $lte = less than or equal
            conditions.append({"amount": amount})

        # Check datetime
        start_date = advanced_filter.get("start_date")
        end_date = advanced_filter.get("end_date")
        if start_date or end_date:
            date_query = {}
            if start_date is not None:
                date_query["$gte"] = handler_datetime(start_date) # $gte = greater than or equal
            if end_date is not None:
                date_query["$lte"] = handler_datetime(end_date) # $lte = less than or equal
            conditions.append({"date": date_query})

        # Check description:
        if "search_text" in advanced_filter:
            conditions.append({
                "description": {
                    "$regex": advanced_filter.get("search_text"),
                    "$options": "i"  # case-insensitive (nghĩa là tùy chọn tìm kiếm không phân biệt chữ hoa/thường)
                }
            })
        return self._add_user_constraint(conditions)

    #Hàm dùng để gộp tất cả điều kiện lọc + điều kiện user_id vào một query, update, delete, find, chỉ trả về document có user_id khớp với self.user_id
    def _add_user_constraint(self, conditions: list) -> dict:
        conditions.append({
            "user_id": ObjectId(self.user_id) if self.user_id else None # thêm điều kiện user_id vào filter, nếu có user_id, nếu không có thì gán None
        })
        return {
            "$and": conditions # "$and" = Gộp tất cả điều kiện vào 1 object dạng $and (dict với key = $and, value = list các điều kiện)
        }

    # Hàm thêm transaction
    def add_transaction(
        self,
        type: str,
        category_id: ObjectId,
        currency: str,
        amount: float,
        date: datetime,
        description: str
    ) -> Optional[str]: # Inserted document ID as string, or None if failed
        """
        Add a new transaction with automatic last_modified timestamp.
        
        Args:
            type: 'Expense' or 'Income'
            category_id: Category ID
            currency: Transaction currency
            amount: Transaction amount
            date: Transaction date
            description: Optional description
        """
        if not isinstance(date, datetime): # Nếu transaction_date KHÔNG phải kiểu datetime
           date = handler_datetime(date) # → thì convert nó thành datetime.

        transaction = {
            'type': type,
            'category_id': category_id,
            'currency': currency,
            'amount': amount,
            'date': date,
            'description': description,
            'created_at': datetime.now(),
            'last_modified': datetime.now(),
            'user_id': self.user_id # added user_id field
        }

        try:
            result = self.collection.insert_one(transaction)
            print("Added transaction successfully", result.inserted_id) # debug
            print(transaction)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return None
    
    def update_transaction(self, transaction_id: str, **kwargs) -> bool:
        """
        Update a transaction and set last_modified timestamp.
        
        Args:
            transaction_id: Transaction ID
            **kwargs: Fields to update
        
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Add last_modified timestamp
            kwargs['last_modified'] = datetime.now() # thêm field "last_modified" vào đúng cái dict kwargs.
            # Build filter and scope by user if available
            filter_ = {'_id': ObjectId(transaction_id),
                       'user_id': self.user_id} # added user_id constraint
            result = self.collection.update_one(filter_, {'$set': kwargs})
            print("Updated transaction successfully", transaction_id)
            print(result)
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return False
        # Với {"$set": transaction_data} Chỉ những field bạn đưa vào transaction_data mới được thay đổi
        # Các field bạn KHÔNG đưa vào giữ nguyên, không bị xóa

    # Hàm xóa transaction theo id
    def delete_transaction(self, transaction_id: str):
        try:
            filter = {"_id": ObjectId(transaction_id), 'user_id': self.user_id} # added user_id constraint
            result = self.collection.delete_one(filter)
            print("Deleted transaction successfully", transaction_id)
            print(result)
            return result.deleted_count > 0 # trả về số document đã xóa (0 hoặc 1) để check nút xóa có thành công không
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False
    
    # Hàm tìm transaction theo id
    def get_transaction_by_id(self, transaction_id: str) -> Optional[dict]:
        """
        Get a single transaction by ID.
        
        Args:
            transaction_id: Transaction ID
        
        Returns:
            Transaction document or None
        """
        try:
            filter_ = {'_id': ObjectId(transaction_id),
                       'user_id': self.user_id} # added user_id constraint
            return self.collection.find_one(filter_)
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None
        
    def get_transactions_by_date_range(
        self,
        start_date: datetime | date | str,
        end_date: datetime | date | str
    ) -> list[dict]:
        """
        Legacy method: Get transactions in date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            list of transaction documents
        """
        return self.get_transactions(
            advanced_filters= {
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    def get_balance_by_date(self, user_id: ObjectId, date: date) -> float:

        # Get target currency (default currency of user)
        target_currency = UserModel().get_default_currency(user_id)

        # lấy list transaction theo ngày
        transactions = list(self.get_transactions(advanced_filters={"user_id": user_id, "start_date": date, "end_date": date}))

         # Exchange currency for transactions in date list
        for t in transactions:
            t["amount"] = ExchangeRateModel().convert_currency(t["amount"], from_currency=t["currency"], to_currency=target_currency)

        # phân ra 2 list: income, expense
        income = [t["amount"] for t in transactions if t["type"] == "Income"]
        expense = [t["amount"] for t in transactions if t["type"] == "Expense"]
        
        if None in income or None in expense:
            balance = "Error when exchange currency"
        else:
            balance = sum(income) - sum(expense)
        return balance
    
    def count_transaction_by_user(self, user_id: ObjectId) -> int:
        return self.collection.count_documents({"user_id": user_id})

'''
if __name__== "__main__":
    print("Init transaction collection")
    transaction = TransactionModel()
    #category_name = category.get_category_name_by_id("692294bf7fb5925a5ef5963e")
    #transaction.count_transactions_by_cate_and_type("Game", "Expense")
    #transaction.count_transactions_by_id_category("692294bf7fb5925a5ef5963e")

    # filter_data = {
    #             "type": "Income",
    #             "currency": "USD",
    #         }
    # transaction.filter_transactions(filters=filter_data)
    #transaction.get_balance_by_date("2023-05-01")
    #transaction.get_transactions(advanced_filters={"start_date": datetime(2025,12,2), "end_date": datetime(2025,12,2)})
    count_transaction_by_user = transaction.count_transaction_by_user("692dd7d3f9d1d3f57cd055aa")
    print(count_transaction_by_user)
#''' 