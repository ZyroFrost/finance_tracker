import pandas as pd
from models.user_model import UserModel
from models.category_model import CategoryModel
from models.transaction_model import TransactionModel
from models.exchange_rate_model import ExchangeRateModel
from utils import get_format_amount
from datetime import datetime, timedelta

class FinanceAnalyzer:
    def __init__(self, user_id: str, user_model: UserModel, category_model: CategoryModel, transaction_model: TransactionModel):
        self.user_model = user_model
        self.user_id = user_id
        self.category_model = category_model
        self.transaction_model = transaction_model
        self.exchange_rate_model = ExchangeRateModel() 
        # Initialize exchange rate model from alanalyzer, no need to initialize from app.py

    def get_filtered_transactions(self, filters: dict):
        """
        Apply filters for transaction page.
        Filters are optional and can be combined.
        """
        transactions = self.transaction_model.get_transactions()

        # ---- TYPE (from tab) ----
        if filters.get("type"):
            transactions = [
                t for t in transactions
                if t.get("type") == filters["type"]
            ]

        # ---- CATEGORY ----
        if filters.get("category_id"):
            transactions = [
                t for t in transactions
                if t.get("category_id") == filters["category_id"]
            ]

        # ---- DATE RANGE ----
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")

        if start_date and end_date:
            # normalize filter dates
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()

            filtered = []
            for t in transactions:
                trans_date = t.get("date")

                # 🔥 normalize transaction date
                if isinstance(trans_date, datetime):
                    trans_date = trans_date.date()

                if start_date <= trans_date <= end_date:
                    filtered.append(t)

            transactions = filtered

        # ---- CURRENCY (FILTER, NOT CONVERT) ----
        if filters.get("currency"):
            transactions = [
                t for t in transactions
                if t.get("currency") == filters["currency"]
            ]

        # ---- AMOUNT RANGE (RAW AMOUNT) ----
        min_amount = filters.get("min_amount")
        max_amount = filters.get("max_amount")

        if min_amount and min_amount > 0:
            transactions = [
                t for t in transactions
                if t.get("amount", 0) >= min_amount
            ]

        if max_amount and max_amount > 0:
            transactions = [
                t for t in transactions
                if t.get("amount", 0) <= max_amount
            ]

        return transactions

    # Map category id to category name
    def map_category_names(self, df):
        categories = self.category_model.get_categories()
        cate_map = {str(c["_id"]): c["name"] for c in categories}
        df["category_id"] = df["category_id"].astype(str)
        df["category"] = df["category_id"].map(cate_map)
        return df

    def normalize_amount_to_user_currency(self, amount: float, from_currency: str) -> float:
        """
        Convert amount from its original currency
        to user's default currency (stored internally)
        Return NUMBER only (no format)
        """
        default_currency = self.user_model.get_default_currency(self.user_id)
        converted_amount = self.exchange_rate_model.convert_currency(amount, from_currency, default_currency)
        return converted_amount

    # Format amount
    def format_amounth_currency_for_user(self, amount, from_currency):
        """
        Convert amount to user's default currency, and format amount with currency 
        """
        # Get default currency from user
        default_currency = self.user_model.get_default_currency(self.user_id)

         # Get exchange rate
        if from_currency == default_currency:
            converted_amount = amount
        else:
            converted_amount = self.exchange_rate_model.convert_currency(amount, from_currency, default_currency)
       
        # Format amount
        format_converted = get_format_amount(default_currency, converted_amount) # format again to get right format
        formatted_original = get_format_amount(from_currency, amount)

        # If from currency is default currency, return original amount for transaction view
        if from_currency == default_currency:
            return format_converted
        
        # Else, return original amount and converted amount, for transaction view
        return f"{format_converted} ({formatted_original})"
        
    # Calculate total amount for a given transaction type
    def calculate_total_by_type(self, transaction_type, start_date=None, end_date=None):
        '''Calculates the total amount for a given transaction type and date range.'''
        if start_date and end_date:
            transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.transaction_model.get_transactions()

        total = 0
        for t in transactions:
            if t["type"] != transaction_type:
                continue

            amount = t["amount"]
            currency = t["currency"]

            # 🔥 convert về default currency
            amount = self.normalize_amount_to_user_currency(amount, currency)

            total += amount

        return total
    
    def calculate_total_by_filter(self, filter: dict):
        '''Calculates the total amount for a given transaction type and date range.'''
        transactions = self.transaction_model.get_transactions(advanced_filters=filter)
        total = sum(t['amount'] for t in transactions)
        return total
    
    def get_spending_by_category(self, start_date=None, end_date=None):
        """Get spending grouped by category"""
        default_currency = self.user_model.get_default_currency(self.user_id)
        exchange = self.exchange_rate_model

        # Lấy giao dịch
        if start_date and end_date:
            transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.transaction_model.get_transactions()

        normalized_transactions = []
        for t in transactions:
            amount = t['amount']
            currency = t['currency']
            converted_amount = exchange.convert_currency(amount, from_currency=currency, to_currency=default_currency)

            t_copy=t.copy()
            t_copy['amount'] = converted_amount
            t_copy['currency'] = default_currency
            
            normalized_transactions.append(t_copy)

        transactions_converted =  normalized_transactions

        if not transactions:
            return pd.DataFrame()

        # Convert dataframe
        df = pd.DataFrame(transactions_converted)

        # Chỉ lấy expenses — COPY để tránh SettingWithCopyWarning
        expenses = df[df['type'] == 'Expense'].copy()
        if expenses.empty:
            return pd.DataFrame()

        # Chuẩn hoá category_id sang string
        expenses.loc[:, "category_id"] = expenses["category_id"].astype(str)

        # Lấy mapping category_id → name
        categories = self.category_model.get_categories() # Get full categories
        cate_map = {str(c["_id"]): c["name"] for c in categories} # Set a dict with category_id as key and category name as value

        # Map vào expenses (không map vào df)
        expenses.loc[:, "category"] = expenses["category_id"].map(cate_map)
        # .loc[row, column] = truy cập bằng label, : = chọn tất cả các dòng, "category" = chọn một cột tên category
        # .map(cate_map) sẽ thay từng category_id bằng category_name

        # Group theo category name
        category_spending = (
            expenses.groupby("category")["amount"]
            .agg(["sum", "count", "mean"])
            .reset_index()
        )

        # Rename columns
        category_spending.columns = ['Category', 'Total', 'Count', 'Average']

        return category_spending.sort_values("Total", ascending=False)
    
    def get_spent_for_month_by_category(self, category_id, month, year, budget_currency):
        """Get total amount spent for a given month and year"""
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1) # Check if month is December

        filter = {
            "type": "Expense",
            "category_id": category_id,
            "start_date": start_date,
            "end_date": end_date
        }

        # Get transactions
        transactions = self.transaction_model.get_transactions(advanced_filters=filter)

        total = 0
        for t in transactions:
            trans_amount = t['amount']
            trans_currency = t['currency']

            if trans_currency != budget_currency:
                trans_amount = self.exchange_rate_model.convert_currency(trans_amount, trans_currency, budget_currency)

            total += trans_amount

        return total
    
    def get_spent_for_year_by_category(self, category_id, year, budget_currency):
        """Get total amount spent for a given year"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        filter = {
            "type": "Expense",
            "category_id": category_id,
            "start_date": start_date,
            "end_date": end_date
        }

        # Get transactions
        transactions = self.transaction_model.get_transactions(advanced_filters=filter)

        total = 0
        for t in transactions:
            trans_amount = t['amount']
            trans_currency = t['currency']

            if trans_currency != budget_currency:
                trans_amount = self.exchange_rate_model.convert_currency(trans_amount, trans_currency, budget_currency)

            total += trans_amount

        return total
    
    def get_monthly_trend(self, months=6):
        """Get monthly trend"""
        
        end_date = pd.Timestamp.today().normalize()
        start_date = end_date - pd.DateOffset(months=months)

        transactions = self.transaction_model.get_transactions_by_date_range(
            start_date, end_date
        )

        if not transactions:
            return pd.DataFrame()

        df = pd.DataFrame(transactions)
        df["date"] = pd.to_datetime(df["date"])

        # normalize currency
        default_currency = self.user_model.get_default_currency(self.user_id)
        df["amount"] = df.apply(
            lambda r: self.exchange_rate_model.convert_currency(
                r["amount"], r["currency"], default_currency
            ),
            axis=1
        )

        df["month"] = df["date"].dt.to_period("M")

        monthly = (
            df.groupby(["month", "type"])["amount"]
            .sum()
            .unstack(fill_value=0)
        )

        # 🔥 QUAN TRỌNG: ép index thành string
        monthly.index = monthly.index.astype(str)

        return monthly

    def get_daily_average(self):
        """
        Calculate daily average spending
        (converted to user's default currency)
        """
        transactions = self.transaction_model.get_transactions()
        expenses = [t for t in transactions if t['type'] == 'Expense']

        if not expenses:
            return 0

        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])

        date_range = (df['date'].max() - df['date'].min()).days + 1
        if date_range <= 0:
            return 0

        # 🔥 DÙNG CHUNG LOGIC ĐÃ CONVERT
        total_spending = self.calculate_total_by_type("Expense")

        return total_spending / date_range
    
    def compare_periods(self, start_date: datetime, end_date: datetime, transaction_type=None):
        """
        Compare total income/expense/net between:
        - current period (start_date → end_date)
        - previous period of same length
        
        transaction_type:
            'Income', 'Expense', None = Net Balance
        """
        # --- Period length ---
        days = (end_date - start_date).days - 1
        print(days)
        
        # --- Previous period ---
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days - 1)

        # --- Current value ---
        current_transactions = self.transaction_model.get_transactions_by_date_range(start_date, end_date)

        # --- Previous value ---
        prev_transactions = self.transaction_model.get_transactions_by_date_range(prev_start, prev_end)

        # Filter type if needed
        if transaction_type:
            current_value = sum(t['amount'] for t in current_transactions if t['type'] == transaction_type)
            prev_value = sum(t['amount'] for t in prev_transactions if t['type'] == transaction_type)
        else:
            # Net balance = income - expense
            current_income = sum(t['amount'] for t in current_transactions if t['type'] == 'Income')
            current_expense = sum(t['amount'] for t in current_transactions if t['type'] == 'Expense')
            current_value = current_income - current_expense

            prev_income = sum(t['amount'] for t in prev_transactions if t['type'] == 'Income')
            prev_expense = sum(t['amount'] for t in prev_transactions if t['type'] == 'Expense')
            prev_value = prev_income - prev_expense

        # --- Percent change ---
        if prev_value == 0:
            percent_change = None
        else:
            percent_change = ((current_value - prev_value) / prev_value) * 100

        trend = "up" if percent_change and percent_change > 0 else "down"

        return {
            "current": current_value,
            "previous": prev_value,
            "percent": percent_change,
            "trend": trend,
            "period_days": days
        }   
