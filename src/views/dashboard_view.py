from assets.styles import container_page_css, container_main_css
from models.transaction_model import TransactionModel
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinanceVisualizer
from utils import get_format_amount, get_date_range_options

from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css

import streamlit as st
import pandas as pd
import numpy as np

# ======== CACHE FUNCTIONS =========
@st.cache_data(ttl=300)
def get_cached_dashboard_metrics(user_id: str, start_date, end_date):
    """Cache dashboard metrics for 5 minutes"""
    from analytics.analyzer import FinanceAnalyzer
    models = st.session_state["models"]
    
    analyzer = FinanceAnalyzer(
        user_id, 
        models["user"], 
        models["category"], 
        models["transaction"]
    )
    
    if start_date and end_date:
        total_income = analyzer.calculate_total_by_type('Income', start_date, end_date)
        total_expense = analyzer.calculate_total_by_type('Expense', start_date, end_date)
    else:
        total_income = analyzer.calculate_total_by_type('Income')
        total_expense = analyzer.calculate_total_by_type('Expense')
    
    net_balance = total_income - total_expense
    daily_average = analyzer.get_daily_average()
    
    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'daily_average': daily_average
    }

@st.cache_data(ttl=300)
def get_cached_category_spending(user_id: str, start_date, end_date):
    """Cache category spending for 5 minutes"""
    from analytics.analyzer import FinanceAnalyzer
    models = st.session_state["models"]
    
    analyzer = FinanceAnalyzer(
        user_id, 
        models["user"], 
        models["category"], 
        models["transaction"]
    )
    
    return analyzer.get_spending_by_category(start_date, end_date)

@st.cache_data(ttl=300)
def get_cached_monthly_trend(user_id: str, months=6):
    """Cache monthly trend for 5 minutes"""
    from analytics.analyzer import FinanceAnalyzer
    models = st.session_state["models"]
    
    analyzer = FinanceAnalyzer(
        user_id, 
        models["user"], 
        models["category"], 
        models["transaction"]
    )
    
    return analyzer.get_monthly_trend(months)

# ======== CONFIG =========
def render_line_chart():
    st.markdown("**Trending**")

    dates = pd.date_range("2025-01-01", periods=10) # Tạo chuỗi ngày (Date)
    
    # Tạo dữ liệu chi tiêu (Amount) ngẫu nhiên
    data = {
        'Date': dates,
        # Sử dụng cumsum (tích lũy) để tạo xu hướng tăng/giảm cho chi tiêu
        'Daily_Expense': np.random.randint(10, 50, size=10),
        'Daily_Income': np.random.randint(40, 70, size=10)
    }
    
    df = pd.DataFrame(data)
    df = df.set_index('Date') # Đặt cột 'Date' làm index (tốt cho biểu đồ đường)

    #st.subheader("Dữ liệu 10 ngày gần nhất:")
    #st.dataframe(df)

    # 2. VẼ BIỂU ĐỒ (Sử dụng hàm st.line_chart())
    #st.markdown("---")
    st.caption("Biểu đồ thể hiện sự thay đổi giữa Thu nhập và Chi tiêu theo thời gian.")
    
    # Vẽ biểu đồ đường, Streamlit sẽ tự động dùng Index (Date) làm trục X
    st.line_chart(df) 
    
    # HOẶC bạn có thể chỉ định rõ ràng cột Y muốn vẽ:
    # st.line_chart(df['Daily_Expense'])

# ======== RENDER DASHBOARD ==========
def render_dashboard_func_panel():
    _, cFilter = st.columns([1, 1])

    # Filter popover
    with cFilter:
        with st.popover("Filter", icon="🔎", use_container_width=True):    
            
            # Select date range
            st.select_slider("📅 Date Range Option", options=list(get_date_range_options().keys()), value="Last 30 Days", key="dashboard_date_range") # set default = "All Time"

def render_metric(analyzer: FinanceAnalyzer, start_date, end_date):
    """Render the metrics cards at the top of dashboard"""
    default_currency = analyzer.user_model.get_default_currency(analyzer.user_id)
    
    # 🔥 Use cached metrics
    metrics = get_cached_dashboard_metrics(
        str(analyzer.user_id),
        start_date,
        end_date
    )

    # Render metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Income", get_format_amount(default_currency, metrics['total_income']), border=True)
    with col2:
        st.metric("💸 Total Expense", get_format_amount(default_currency, metrics['total_expense']), border=True)
    with col3:
        st.metric("💳 Net Balance", get_format_amount(default_currency, metrics['net_balance']), border=True)
    with col4:
        st.metric("📊 Daily Average", get_format_amount(default_currency, metrics['daily_average']), border=True)

def render_charts(analyzer_model: FinanceAnalyzer, visualizer_model: FinanceVisualizer, start_date, end_date, currency):
    """Render the charts section with category and trend visualizations"""
    # Category chart
    col1, col2 = st.columns(2)

    with col1:
        # st.subheader("Category Spending")
        #category_spending = analyzer_model.get_spending_by_category(start_date, end_date)
        category_spending = get_cached_category_spending(str(st.session_state.user_id), start_date, end_date)

        if not category_spending.empty:
            fig = visualizer_model.plot_category_spending(category_spending, currency)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No expense data available for this period")
    
    with col2:
        # st.subheader("Category Breakdown")
        if not category_spending.empty:
            fig = visualizer_model.plot_pie_chart(category_spending)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No expense data available for this period")
        
    st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 1px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

    # Monthly trend
    st.subheader("Monthly Trend")
    #monthly_trend = analyzer_model.get_monthly_trend(months=6)
    monthly_trend = get_cached_monthly_trend(str(st.session_state.user_id), months=6)

    if not monthly_trend.empty:
        fig = visualizer_model.plot_monthly_trend(monthly_trend, currency)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No data available for monthly trend")

def render_dashboard(analyzer_model: FinanceAnalyzer, transaction_model:TransactionModel, visualizer_model: FinanceVisualizer):
    models = st.session_state["models"]   # Lấy model từ App.py
    transaction_model = models["transaction"]
    visualizer_model = models["visualizer"]

    # Get default currency for user
    default_currency = models["user"].get_default_currency(st.session_state.user_id)

    with stylable_container(key="content_box", css_styles=container_page_css()):

        # Header
        cHeader, cFunc = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Dashboard")         
        with cFunc:
            render_dashboard_func_panel()

        # Line ngang sát menu
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)
        
        with stylable_container(key="main_box", css_styles=container_main_css()):

            transaction_count = transaction_model.count_transaction_by_user(st.session_state.user_id)
            if transaction_count == 0:
                st.subheader("You have no transaction data yet. Please add some transactions to see the dashboard.")
                st.stop()

            # Metric
            date_range_option = st.session_state.dashboard_date_range
            date_ranges = get_date_range_options() #> return dictionary
            start_date, end_date = date_ranges[date_range_option]
            render_metric(analyzer_model, start_date, end_date)

            st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 1px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

            # Charts
            render_charts(analyzer_model, visualizer_model, start_date, end_date, default_currency)