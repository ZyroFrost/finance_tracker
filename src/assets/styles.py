from core import config
import streamlit as st

def set_global_css():
    # Set page config phải đặt đầu tiên, nếu nằm sau st nào khác thì sẽ báo lỗi
    st.set_page_config(
        page_title=config.APP_NAME,
        layout="wide",
        page_icon="src/assets/icon.png",
        initial_sidebar_state="expanded",
        menu_items={'About': f'{config.APP_NAME} \n'})

# Chỉnh màu cho cục bộ toàn app (màu xám) #EEEEEE = xám nhẹ
    st.markdown("""<style>.stApp {background-color: white;}</style>""", unsafe_allow_html=True)

    # chỉnh rộng màn hình
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0rem;
                padding-bottom: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # xóa header, footer
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            header .stAppHeader {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

def container_page_css():
    # tùy chỉnh cho phần menu
    page =  """
        {
            background-color: white;
            border-radius: 12px;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            min-height: 80vh !important;
            align-items: left; /* Canh giữa dọc */
        }
    """
    return page

def container_main_css():
    body_style = """
        {   
            min-height: 69vh !important;
            max-height: 69vh !important;
            overflow-y: auto; /* Nếu nội dung dài thì cuộn bên trong khung */
        }
    """
    return body_style

# Detail category 
def container_detail_category_css():
    detail_style = """
        {
            background-color: #EEEEEE;
            border-radius: 10px;
            border: 1px solid gray;
            padding: 22px;
            box-shadow: 0 0 8px rgba(0,0,0,0.2);
            /* min-height: 12.5vh !important; */
            /* max-height: 12.5vh !important; */
        }
    """
    return detail_style 

# def container_detail_budget_css():
#     detail_style = """
#         {
#             background-color: #EEEEEE;
#             border-radius: 10px;
#             border: 1px solid gray;
#             padding: 22px;
#             box-shadow: 0 0 8px rgba(0,0,0,0.2);
#             /* min-height: 12.5vh !important; */
#             /* max-height: 12.5vh !important; */
#         }
#     """
#     return detail_style 

def option_menu_css():
    # Tùy chỉnh cho option_menu
    {"container": {"padding": "5 !important", "background-color": "#FFFFFF", "border-radius": "15px"},}

def google_icon_css():
    # css cho icon Google
    st.markdown("""
    <style>
    img[alt="icon"] {
        max-width: 40px !important;
        max-height: 40px !important;
        width: auto !important;
        height: auto !important;
        object-fit: contain !important;
    }
    </style>
    """, unsafe_allow_html=True)

# hàm tạo cấu trúc card transaction
def transaction_card_css(type: str, category: str, amount_currency: str, description: str, icon: str , created, modified):
    arrow = "+" if type == "Income" else "-"
    color = "#1caa57" if type == "Income" else "#e74c3c"

    st.markdown(f"""
    <div style="
        padding: 12px;
        border-radius: 10px;
        border: 0px solid #ddd;
        background: white;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    ">
        <div style="display:flex; width:100%;"> <!-- width 100% để full khung ko bị lệch-->
            <!-- LEFT COLUMN -->
            <div style="flex: 0.5;"> <!-- flex = phân bổ chiều rộng của cột, tương tự st.columns([1,1])-->
                <div style="font-size:14px;color:#555;"><strong>{description}</strong></div>
                <!-- <span style="font-size:14px;color:#555;">Category: </span> -->
                <span style="font-size:14px;color:#555;">{icon} {category}  </span>
            </div>
            <!-- MIDDLE COLUMN -->
            <div style="flex: 1; text-align:left;">
                <div style="font-size:28px;color:{color};font-weight:700;">{arrow} {amount_currency}</div>
            </div>
            <!-- RIGHT COLUMN -->
            <div style="flex: 0.5; text-align:right;">
                <div style="font-size:14px;color:#555;">Created: {created}</div>
                <div style="font-size:14px;color:#555;">Last modified: {modified}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def transaction_expander_css():
    # background color
    color_when_close = "#b9b9b9"
    color_when_open = "#CAC4B4"
    color_background = "#ffffff"

    # text color
    color_text_when_close = "#000000"

    # css
    css = f"""
    <style>
    div[data-testid="stExpander"] > details > summary {{
        background-color: {color_when_close} !important;
        color: {color_text_when_close} !important;
        font-weight: 600;
        border-radius: 6px;
        padding: 8px;
    }}
    div[data-testid="stExpander"] > details[open] > summary {{
        background-color: {color_when_open} !important;
    }}

    div[data-testid="stExpander"] > details > div {{
        background-color: {color_background} !important;
        padding: 10px;
        border-radius: 6px;
    }}
    </style>
    """
    st.html(css)

# hàm đổi màu progress bar theo ratio, ko dùng dc vì hàm st.progress() ko nhận màu riêng lẻ từng processbar được, chỉ đổi dc màu cục bộ
# def get_progress_css(percent: float) -> str:
#     if percent < 0.7:
#         color = "#2ecc71"   # xanh
#     elif percent < 1.0:
#         color = "#f39c12"   # cam
#     else:
#         color = "#e74c3c"   # đỏ

#     return f"""
#     <style>
#     .stProgress > div > div > div > div {{
#         background-color: {color};
#     }}
#     </style>
#     """

# progress bar tạo bằng html css
def render_budget_progress(percent: float):
    if percent < 0.7:
        color = "#2ecc71"
    elif percent < 1.0:
        color = "#f39c12"
    elif percent == 1.0:
        color = "#f39c12"
    else:
        color = "#e74c3c"

    width = min(percent * 100, 100)

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 0.5rem;
            background: #eee;
            border-radius: 6px;
            overflow: hidden;
            margin: 6px 0;
        ">
            <div style="
                width: {width}%;
                height: 100%;
                background: {color};
                transition: width 0.3s ease;
            "></div>
        </div>
        """,
        unsafe_allow_html=True
    )