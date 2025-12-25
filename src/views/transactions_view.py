from models.user_model import UserModel
from models.category_model import CategoryModel
from models.transaction_model import TransactionModel
from analytics.analyzer import FinanceAnalyzer

from utils import get_format_amount, get_format_currency, get_date_range_options, get_type_list, get_currencies_list, state_input, format_date
from assets.styles import container_page_css, container_main_css, transaction_card_css
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
from datetime import datetime
import streamlit as st       

# ======== DiALOGS =========
def delete_transaction_dialog(transaction_model: TransactionModel):
    dialog_name = st.session_state.trans_confirm_delete # lấy name của transaction từ session state (phần nút xóa)
    trans_id = st.session_state.trans_confirm_delete_id # lấy id của transaction (dùng để đưa vào hàm khi confirm)
    print(dialog_name)

    @st.dialog(f"Transaction '{dialog_name}' will be deleted. Are you sure you want to delete?") # Tạo dialog xác nhận xóa transaction
    def trans_dialog():
        cCancel, cConfirm = st.columns(2)

        if cCancel.button("❌ Cancel", use_container_width=True):
            st.session_state.trans_confirm_delete = None # Tắt dialog confirm
            st.session_state.trans_confirm_delete_id = None
            st.rerun()

        if cConfirm.button("✅ Confirm", use_container_width=True):
            result = transaction_model.delete_transaction(trans_id) # Xóa transaction

            # Tắt dialog confirm
            st.session_state.trans_confirm_delete = None
            st.session_state.trans_confirm_delete_id = None

            # Mở dialog message
            if result: # nếu xóa thanh cong
                st.session_state.delete_trans_success = dialog_name # gán trạng thái xóa thanh cong thành = name (delete_trans_success = trans_confirm_delete)
            else:
                st.session_state.delete_trans_failed = dialog_name
            st.rerun()     
    trans_dialog()
# ======== END DiALOGS =========

# ======== MAIN RENDER =========
def render_trans_func_panel(category_model: CategoryModel, transaction_model: TransactionModel):

    cAddTrans, cFilter = st.columns([1, 1])
    with cAddTrans:
        # Add new transaction
        with st.popover("➕ Add Transaction", use_container_width=True):

            # Select type
            trans_type_add = st.selectbox("Select Type", get_type_list(), key="trans_type_add")

            # Select category
            st.selectbox("Select Category", category_model.get_category_name_by_type(st.session_state.get("trans_type_add")), key="trans_cate_add")
            trans_cate_id = category_model.get_category_id_by_name(st.session_state.get("trans_cate_add")) # transform name to id for saving

            # Select Currency
            trans_currencies = st.selectbox("Currency", get_currencies_list(), key="trans_currencies") # Lấy list currencies từ config

            # currencies của VN ko xài phân số (float) nhưng USD thì có, nên nếu set thông số trực tiếp sẽ bị lỗi ko đồng bộ 2 loại dữ liệu,
            # nên phải xét riêng, VND (step=500, format="%d", min_value=0) 3 cái này chung là int, còn 3 cái của USD chung là float
            current_currencies = st.session_state.get("trans_currencies")
            trans_currency_format = get_format_currency(current_currencies) # Lấy format theo currencies
            currencies_step, currencies_format, min_value = trans_currency_format
            trans_amount = st.number_input("Amount", key="amount", step=currencies_step, min_value=min_value, format=currencies_format) # amout, base on currencies

            # Input Description
            trans_description = st.text_area("Description", key="new_trans_description")                 

            # Date input, Vì json lưu dạng ngày + time, nhưng hàm date_input chỉ nhận ngày, nên phải thêm giờ tự động 0:00
            trans_date = st.date_input("Date", key="new_trans_date")

            # Button
            if st.button("✔️ Comfirm", use_container_width=True):
                if not trans_date:
                    st.error("Date is required!")
                elif trans_amount <= min_value:
                    st.error("Amount is required!")
                elif not trans_description or trans_description.strip() == "":
                    trans_description = "No description"
                else:              
                    transaction_model.add_transaction(
                        type=trans_type_add, 
                        category_id=trans_cate_id, 
                        currency=trans_currencies,
                        amount=trans_amount, 
                        date=trans_date, 
                        description=trans_description
                    )
                    st.session_state["transaction_added"] = True
                    st.rerun()

            # Confirmation message
            if st.session_state.get("transaction_added") == True:
                st.success("Transaction added successfully!")
                st.session_state["transaction_added"] = False

    # Filter popover
    with cFilter:
        with st.popover("Filter", icon="🔎", use_container_width=True):    

            # Select category
            categories = category_model.get_categories()
            # Add "All" option at the beginning
            all_option = {"_id": None, "name": "All"}
            categories_with_all = [all_option] + categories
            
            st.selectbox(
                "📦 Category Name", 
                options=categories_with_all, 
                format_func=lambda c: c["name"], 
                key="select_category2"
            )
            
            # Select date range
            date_option = get_date_range_options()
            st.select_slider("📅 Date Range Option", options=list(date_option.keys()), key="date_range2")

            # Select currency
            currency_all_option = {"_id": None, "name": "All"}

            currencies = get_currencies_list()
            # nếu currency là string → convert thành dict
            currencies = [{"_id": c, "name": c} for c in currencies]

            currencies_with_all = [currency_all_option] + currencies
            st.selectbox("💰 Currency", options=currencies_with_all, format_func=lambda c: c["name"], key="currency2")

            # Select amount
            min, max = st.columns(2)
            with min:
                st.number_input("🔽 Minimum Amount", min_value=0, value=0, key="min_amount2")
            with max:
                st.number_input("🔼 Maximum Amount", min_value=0, value=0, key="max_amount2")

            # Data dict
            filter_data = {
                "category_id": st.session_state.get("select_category2"),
                "date_range": st.session_state.get("date_range2"),
                "currency": st.session_state.get("currency2"),
                "min_amount": st.session_state.get("min_amount2"),
                "max_amount": st.session_state.get("max_amount2"),
            }

            bClear, bFilter = st.columns(2)

            if bClear.button("❌ Clear Filter", use_container_width=True):
                st.session_state.trans_filter_applied = False
                st.session_state.trans_filter_data = {}
                st.rerun()

            # Button filter
            if bFilter.button("🔎 Search", use_container_width=True):
                normalized_filter = {}

                # category - Only add if not "All"
                selected_category = filter_data["category_id"]
                if selected_category and selected_category.get("_id") is not None:
                    normalized_filter["category_id"] = selected_category["_id"]

                # date range
                date_ranges = get_date_range_options()
                if filter_data["date_range"] in date_ranges:
                    start_date, end_date = date_ranges[filter_data["date_range"]]
                    normalized_filter["start_date"] = start_date
                    normalized_filter["end_date"] = end_date

                # currency - Only add if not "All"
                selected_currency = filter_data["currency"]
                if selected_currency and selected_currency.get("_id") is not None:
                    normalized_filter["currency"] = selected_currency["name"]

                # amount
                if filter_data["min_amount"] > 0:
                    normalized_filter["min_amount"] = filter_data["min_amount"]

                if filter_data["max_amount"] > 0:
                    normalized_filter["max_amount"] = filter_data["max_amount"]

                # save state
                st.session_state.trans_filter_applied = True
                st.session_state.trans_filter_data = normalized_filter

# Render transaction details
def render_trans_details(user_model: UserModel, category_model: CategoryModel, transaction_model: TransactionModel, analyzer_model: FinanceAnalyzer, category_type):
    # ---- GET FILTER DATA ----
    filters = {}

    # Apply filter from Search
    if st.session_state.get("trans_filter_applied"):
        filters.update(st.session_state.get("trans_filter_data", {}))

    # Apply type from tab
    if category_type != "All":
        filters["type"] = category_type


    with stylable_container(key=category_type, css_styles=container_main_css()):

        # Repare filter
        filters = {}
        if st.session_state.get("trans_filter_applied"):
            filters.update(st.session_state.get("trans_filter_data", {}))

        if category_type != "All":
            filters["type"] = category_type
        
        # Get transactions
        all_trans = analyzer_model.get_filtered_transactions(filters)
        default_currency = user_model.get_default_currency(st.session_state.user_id)

        # Variable, cái này test tối ưu, lấy all trans (cached) 1 lần để khỏi gọi lên DB nhiều lần, chưa xử lý xuông dưới
        if category_type == "All":
            trans_list_by_type = all_trans
        else:
            trans_list_by_type = [t for t in all_trans if t["type"] == category_type]

        # dates list sort descending and unique to loop
        dates = list(sorted({t["date"] for t in trans_list_by_type}, reverse=True))

        if all_trans:
            if "expand_all" not in st.session_state:
                st.session_state.expand_all = False
            
            def set_expand_all(value: bool):
                st.session_state.expand_all = value

            cTotal, cExpanderOpen, cExpanderClose = st.columns([7, 1, 1])
            with cTotal:
                st.write(f"{category_type} Transactions — Total: {len(trans_list_by_type)}")
                st.write("")

            # Expander open
            with cExpanderOpen:
                st.button("Expand All", width="stretch", key=f"{category_type}_expand_all", on_click=set_expand_all, args=(True,))

            with cExpanderClose:
                st.button("Collapse All", width="stretch", key=f"{category_type}_collapse_all", on_click=set_expand_all, args=(False,))

            # for loop by dates
            # 🔥 OPTIMIZED: Group transactions by date in memory
            from collections import defaultdict
            trans_by_date_dict = defaultdict(list)
            for t in trans_list_by_type:
                trans_by_date_dict[t["date"]].append(t)

            # for loop by dates
            for d in dates:
                trans_by_date_and_type = trans_by_date_dict.get(d, [])

                # Get balance and format
                balance = transaction_model.get_balance_by_date(user_id=st.session_state.user_id, date=d)
                balance_abs = get_format_amount(default_currency, abs(balance))

                # Display balance (add + or -)
                if balance < 0:
                    display_balance = f"- {balance_abs}"
                elif balance > 0:
                    display_balance = f"+ {balance_abs}"
                else:
                    display_balance = balance_abs
                
                # format date in expander Date
                formatted_date = format_date(d) # format date for view
                format_count = len(trans_by_date_and_type)

                # render date and balance
                with st.expander(f"{formatted_date} — {format_count} transactions — Balance: {display_balance}", expanded=st.session_state.expand_all):             

                    # Transactions in dates
                    for idi, item in enumerate(trans_by_date_and_type): 

                        # custom items, đặt ở ngoài để dùng chung
                        type = item.get('type')
                        category_name = category_model.get_category_name_by_id(item.get('category_id')) # dò category name theo category id
                        description = item.get('description')
                        
                        # Convert currency then format
                        amount_format = analyzer_model.format_amounth_currency_for_user(item.get('amount'), item.get('currency'))

                        # Icon
                        icon = category_model.get_category_by_id(item.get('category_id')).get('icon')

                        # Date
                        created_at = item.get('created_at').strftime('%d-%m-%Y')
                        last_modified = item.get('last_modified').strftime('%d-%m-%Y')                      
                        
                        # Render
                        with st.container():
                            cDetail, cButton = st.columns([6, 1])
                            with cDetail:
                                transaction_card_css(
                                    type=type,
                                    category=category_name,
                                    amount_currency=amount_format,
                                    description=description,
                                    icon=icon,
                                    created=created_at,
                                    modified=last_modified
                                )

                            with cButton:
                                st.write("") # đẩy xuống
                                cEdit, cDelete = st.columns(2)
                                with cEdit:   
                                    with st.popover("✏️"):        
                                        # Set key ra ngoài
                                        key_type = f"edit_type_{category_type}_{item['_id']}"
                                        key_cate = f"edit_cate_{category_type}_{item['_id']}" 
                                        key_description = f"edit_description_{category_type}_{item['_id']}"
                                        key_currency = f"edit_currency_{category_type}_{item['_id']}"       
                                        key_amount = f"edit_amount_{category_type}_{item['_id']}"
                                        key_date = f"edit_date_{category_type}_{item['_id']}"                                         

                                        col1, col2 = st.columns([1,1])
                                        with col1:

                                            # Set default type by current item's type                            
                                            change_type = state_input(label="Change type", current_data=item["type"], widget=st.selectbox, key=key_type, options=get_type_list()) 

                                            # Set default amount by current item's amount                  
                                            currencies_step, currencies_format, min_value = get_format_currency(item["currency"])
                                            
                                            change_amount = state_input(label="Change amount",
                                                                        current_data=item["amount"], 
                                                                        widget=st.number_input, 
                                                                        key=key_amount, 
                                                                        min_value=min_value,
                                                                        step=currencies_step, 
                                                                        format=currencies_format)  
                                            
                                            # Set default description by current item's description
                                            change_description = state_input(label="Change description", 
                                                                            current_data=item["description"], 
                                                                            widget=st.text_area, 
                                                                            key=key_description)    
                                                
                                        with col2:
                                            # Set category list by current item's category                             
                                            cate_dict = category_model.get_category_by_type(st.session_state[key_type]) 
                                            cate_list = {c["name"]: c["_id"] for c in cate_dict} # trả về list đã if elfe ở trên, keys là lấy value (value là tên từng cate)
                                            cate_edit_options = cate_list.keys()

                                            # Set default category by current item's category
                                            change_cate_name = st.selectbox("Change category", options=cate_edit_options, key=key_cate)
                                            change_cate_id = cate_list.get(change_cate_name) # lấy category id theo name              

                                            # Set default currency list by current item's currency                                                                                                                                     
                                            change_currency = state_input(label="Change currency", 
                                                                        current_data=item["currency"], 
                                                                        widget=st.selectbox, 
                                                                        key=key_currency, 
                                                                        options=get_currencies_list())          

                                            # Set default date by current item's date
                                            st.date_input("Change date", item["date"], key=key_date)        
                                            change_date = datetime.combine(st.session_state[key_date], datetime.min.time())                                                                                                                            

                                            # Update transaction
                                            if st.button("✅ Save", key=f"edit_button_{category_type}_{item['_id']}", use_container_width=True):
                                                if change_description == item['description'] and change_amount == item['amount'] and change_cate_id == item['category_id'] \
                                                and change_currency == item['currency'] and change_type == item['type'] and change_date == item['date']:
                                                    st.error("No changes were made.")
                                                else:
                                                    transaction_model.update_transaction(
                                                        item['_id'], 
                                                        type=change_type, 
                                                        category_id=change_cate_id, 
                                                        description=change_description, 
                                                        currency=change_currency, 
                                                        amount=change_amount,
                                                        date=change_date
                                                    )
                                                    st.session_state[f"edit_trans_success_{category_type}_{item['_id']}"] = True 
                                                    st.rerun()

                                        with cDelete:
                                            if st.button("🗑️", key=f"delete_trans_{category_type}_{item['_id']}"):                        
                                                st.session_state.trans_confirm_delete = item['description']
                                                st.session_state.trans_confirm_delete_id = item['_id']
                                                st.rerun()

                                        # Message after update
                                        if st.session_state.get(f"edit_trans_success_{category_type}_{item['_id']}"): # nhận state edit thành công
                                            st.success(f"Transaction '{item['description']}' updated successfully!")
                                            st.session_state[f"edit_trans_success_{category_type}_{item['_id']}"] = False # reset state

                        # HORIZONTAL LINE
                        if idi < len(trans_by_date_and_type) - 1: # ko in dòng cuối                   
                            st.markdown("""<hr style="margin: 0px 0; border: none; border-top: 1px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)                                      
        else:
            st.subheader("No transactions found.")

# Main Render, call all render
def render_transactions(analyzer_model: FinanceAnalyzer):
    models = st.session_state["models"]
    user_model = models["user"]
    category_model = models["category"]
    transaction_model = models["transaction"]

    with stylable_container(key="menu_box", css_styles=container_page_css()):

        # Header
        cHeader, cFunc = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Transactions")
        with cFunc:
            render_trans_func_panel(category_model, transaction_model)

        # Line
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

        # Main
        # Force reset to "All" tab when navigating to Transactions page
        if st.session_state.get("current_page") == "Transactions":
            if "trans_tab_initialized" not in st.session_state:
                st.session_state.trans_tab_initialized = True
                # Force rerun to ensure All tab is selected
                if st.session_state.get("active_tab") != 0:
                    st.session_state.active_tab = 0
                    st.rerun()

        if "active_tab" not in st.session_state:
            st.session_state.active_tab = 0  # Index 0 = "All"

        tab_names = ["All", "Expense", "Income"]
        tabs = st.tabs(tab_names)

        # Render tất cả tabs
        for (tab, tab_name) in zip(tabs, tab_names):
            with tab:
                render_trans_details(user_model, category_model, transaction_model, analyzer_model, category_type=tab_name)

        # Dialog
        render_trans_dialog(transaction_model)

# Render dialog
def render_trans_dialog(transaction_model):
    if st.session_state.get("trans_confirm_delete"): # Đặt cuối trang
        delete_transaction_dialog(transaction_model)

    if st.session_state.get("delete_trans_success"):
        dialog_name = st.session_state.delete_trans_success

        @st.dialog("Success!")
        def trans_success():
            st.success(f"Transaction '{dialog_name}' deleted successfully!")
            _, cClose = st.columns([5, 1])
            if cClose.button("Close", use_container_width=True):
                st.session_state.delete_trans_success = None # gán none để tắt
                st.rerun()
        trans_success()

    if st.session_state.get("delete_trans_failed"): 
        dialog_name= st.session_state.delete_trans_failed

        @st.dialog(f"Error")
        def trans_failed():
            st.error(f"Failed to delete transaction '{dialog_name}'!")     
            _, cClose = st.columns([5, 1]) # đẩy nút close qua bên phải dialog
            if cClose.button("Close"):
                st.session_state.delete_trans_failed = None
                st.rerun()
        trans_failed()