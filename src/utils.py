# utils.py = file chứa hàm tiện ích dùng chung cho toàn bộ project, ko dính DB, ko dính network, chỉ xử lý dữ liệu đơn thuần
from datetime import datetime, timedelta, date
from core import config
import streamlit as st

# Hàm định dạng số thành dạng tiền tệ
def get_format_amount(currency: str, amount: float):
    """Format number as currency""" 
    currency_info = config.CURRENCIES[currency]
    symbol = currency_info["symbol"]
    decimals = currency_info["decimal_places"]
    position = currency_info["symbol_position"]
    thousand_sep = currency_info["separator_thousand"]
    decimal_sep = currency_info["separator_decimal"]

    # Format number
    if decimals == 0:
        format_number = f"{int(amount):,}"
    else:
        format_number = f"{amount:,.{decimals}f}"

    # Replace decimal separator and thousand separator
    sep_format_number = format_number.replace(",", "X").replace(".", decimal_sep).replace("X", thousand_sep)
    
    # Set symbol position
    if position == "prefix":
        return f"{symbol}{sep_format_number}"
    elif position == "suffix":
        return f"{sep_format_number}{symbol}"

# Hàm định dạng số tiền theo loại tiền tệ, trả về chuỗi định dạng, step và min_value
def get_format_currency(currency: str) -> tuple[float | int, str, float | int]:
    info = config.CURRENCIES[currency]
    if not info:
        raise ValueError(f"Unsupported currency: {currency}")

    return info["step"], info["format"], info["min_value"]

# Hàm lấy các tùy chọn khoảng ngày cho filter

def get_month_name(month: int) -> str:
    return date(2024, month, 1).strftime("%B")

def get_date_range_options():
    """Get predefined date range options"""
    now = datetime.now()
    today = datetime.now().date()
    min_date = date(2020, 1, 1)
    
    # cấu trúc của dictionary: "Option Name": (start_date, end_date)
    return {
        "Today": (today, now),
        "Yesterday": (today - timedelta(days=1), now),
        "Last 7 Days": (today - timedelta(days=7), now),
        "Last 30 Days": (today - timedelta(days=30), now),
        "This Month": (today.replace(day=1), now),
        "Last Month": get_last_month_range(),
        "Last 3 Months": (today - timedelta(days=90), today),
        "Last 6 Months": (today - timedelta(days=180), today),
        "This Year": (today.replace(month=1, day=1), today),
        "All Time": (min_date, now)
    }

# Hàm lấy toàn bộ tháng trước
def get_last_month_range():
    """Get date range for last month"""
    today = datetime.now().date()
    first_day_this_month = today.replace(day=1) # → lấy ngày hiện tại, giữ nguyên năm và tháng, chỉ thay day = 1 (2025-03-17 → 2025-03-01)
    last_day_last_month = first_day_this_month - timedelta(days=1) 
    first_day_last_month = last_day_last_month.replace(day=1)
    return (first_day_last_month, last_day_last_month) # → ngày bắt đầu và kết thúc của tháng trước

# Hàm kiểm tra tính hợp lệ của amount
def validate_amount(amount):
    """Validate amount input"""
    try:
        value = float(amount)
        if value <= 0:
            return False, "Amount must be greater than zero"
        return True, value
    except ValueError:
        return False, "Please enter a valid number"

def display_metric_card(title, value, delta=None, delta_color="normal"):
    """Display a metric card"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

# Hàm này dùng để lưu cache kết quả của bất kỳ hàm nào, trong 5 phút. Giảm thời gian xử lý và tiết kiệm request
@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_data_fetch(func, *args, **kwargs): 
    """Cache data fetching functions"""
    return func(*args, **kwargs)

# Hàm chuẩn hóa mọi dạng ngày tháng (datetime, date, string) → thành datetime duy nhất.
def handler_datetime(date_: datetime | date | str) -> datetime:
    """Convert various date formats to datetime object"""
    if isinstance(date_, datetime): # Đã đúng dạng → trả về luôn
        return date_
    elif isinstance(date_, date): # Nếu truyền vào date (không có giờ) → Chuyển thành: datetime với giờ là 00:00:00
        return datetime.combine(date_, datetime.min.time())
    elif isinstance(date_, str): # Nếu truyền vào string → chuyển thành datetime
        try:
            return datetime.fromisoformat(date_) # Nếu là chuỗi thì phải đúng định dạng ISO (YYYY-MM-DD)
        except ValueError:
            raise ValueError("String date must be in ISO format (YYYY-MM-DD)")
    else: # Nếu truyền vào kiểu khác → báo lỗi
        raise TypeError("Unsupported date type")

# Định dạng daytime chuẩn để hiển thị
def format_date(date_obj: datetime) -> str:
    """Format datetime object to string"""
    return date_obj.strftime("%Y-%m-%d")

# Check default category
def is_default_category(category_type: str, category_name: str) -> bool:
    if category_type == "Expense":
        return category_name in config.DEFAULT_CATEGORIES_EXPENSE
    
    if category_type == "Income":
        return category_name in config.DEFAULT_CATEGORIES_INCOME
    
def get_type_list():
    return config.TRANSACTION_TYPES

def get_currencies_list():
    return list(config.CURRENCIES.keys())

# Hàm lấy session state, lấy trạng thái hiện tại của data đưa lên input (cho nút edit):
def state_input(key, current_data, widget, **kwargs):
    if key not in st.session_state: # Nếu chưa có trong session thì set default = type hiện tại
        st.session_state[key] = current_data
    return widget(key=key, **kwargs) 
    # widget → chính là st.selectbox, st.text_input, st.number_input...
    # **kwargs → là các thuộc tính của từng widget (value, label...)

'''
if __name__ == "__main__": # Test function
    print(get_currencies_list())
    get_type_list()
#'''