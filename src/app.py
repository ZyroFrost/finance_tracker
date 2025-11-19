import streamlit as st
from core import config
from models.category_models import CategoryModel
from models.transaction_models import TransactionModel

APP_NAME = config.APP_NAME

# Lần sau rerun → Streamlit không tạo lại DatabaseManager Nó lấy resource đã cache và dùng lại → để tối ưu tốc độ, giảm lag
@st.cache_resource 
def init_category_models():
    return CategoryModel()

@st.cache_resource # tạo trước def để chỉ tạo 1 lần (lần sau gọi trong cache)
def init_transaction_models():
    return TransactionModel()  

cate = init_category_models()
trans = init_transaction_models()



# Set page config phải đặt đầu tiên, nếu nằm sau st nào khác thì sẽ báo lỗi
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="📊",
)

st.header(APP_NAME)

with st.sidebar:
    with st.expander("Goals"):
        st.write("➕ Add New Category")
        st.selectbox("Type of transaction", config.TRANSACTION_TYPES)

col1, col2, col3 = st.columns(3)
with col1:
    st.text("Total Categories") 
    total = cate.count_total()
    st.text(total)

with col2:
    st.text("Expense Transactions")
    expense = cate.get_category_by_type(type="Expense")
    st.text(expense)

with col3:
    st.text("Income Categories")
    income = cate.get_category_by_type(type="Income")
    st.text(income)