from core import config
from models.category_model import CategoryModel
from models.budgets_model import BudgetModel
from analytics.analyzer import FinanceAnalyzer

from utils import get_format_amount, get_format_currency, get_date_range_options, get_type_list, get_currencies_list, state_input, get_month_name
from assets.styles import container_page_css, container_main_css, render_budget_progress
from streamlit_extras.stylable_container import stylable_container # thư viện mở rộng của streamlit để add container với css
from datetime import datetime
import streamlit as st      
# import calendar

# ======== MAIN RENDER =========
def render_budgets_func_panel(category_model: CategoryModel, budget_model: BudgetModel):
    cAddBudget, cFilter = st.columns([1, 1])

    with cAddBudget:
        with st.popover("➕ Add Budget", use_container_width=True):

            # Select category + convert it to name
            st.selectbox("Select Category", category_model.get_category_name_by_type("Expense"), key="budget_cate_add")
            budget_cate_id = category_model.get_category_id_by_name(st.session_state.get("budget_cate_add")) # transform name to id for saving

            # Select budget type
            budget_type = st.selectbox("Budget Type", config.BUDGET_TYPES, key="budget_type")

            # Show month selectbox only if budget type is monthly
            if budget_type == "Monthly":
                # Select month + set month name
                # months = list(calendar.month_name)[1:] # Bỏ index 0 (empty) # lưu int nên bị sai
                months = list(range(1, 13))
                budget_month = st.selectbox("Month", months, key="budget_month")
            else:
                budget_month = None

            # Select year + set current year +- 2
            current_year = datetime.now().year
            budget_year = st.selectbox("Year", list(range(current_year - 2, current_year + 3)), key="budget_year")

            # Select Currency
            budget_currencies = st.selectbox("Currency", get_currencies_list(), key="budget_currencies") # Lấy list currencies tự trong config

            # Select amount + format currencies
            current_currencies = st.session_state.get("budget_currencies")
            budget_currency_format = get_format_currency(current_currencies) # Lấy format theo currencies
            currencies_step, currencies_format, min_value = budget_currency_format
            budget_amount = st.number_input("Amount", key="amount", step=currencies_step, min_value=min_value, format=currencies_format) 

            if st.button("✔️ Comfirm", use_container_width=True):

                if budget_amount <= 0:
                    st.error("Amount is required!")
                else:
                    budgets = budget_model.get_budgets() # Get budgets for validation
                    
                    # Check duplicate for monthly
                    if budget_type == "Monthly":
                        is_duplicate = any(
                            b["category_id"] == budget_cate_id and b["month"] == budget_month and b["year"] == budget_year and b["budget_type"] == budget_type
                            for b in budgets
                        ) 
                    else: # Check duplicate for yearly
                        is_duplicate = any(
                            b["category_id"] == budget_cate_id and b["year"] == budget_year and b["budget_type"] == budget_type
                            for b in budgets
                        )
                    
                    if is_duplicate:
                        msg = "month/year" if budget_type == "Monthly" else "year" # Set message for monthly or yearly
                        st.error(f"Budget already exists for this category and {msg}")
                    else:
                        budget_model.save_budget(None, budget_cate_id, budget_type, budget_currencies, budget_amount, budget_month, budget_year)
                        st.session_state["budget_add_success"] = True
                        st.rerun()

            # Show success message
            if st.session_state.get("budget_add_success") == True:
                st.success("Add budget successfully!")
                st.session_state["budget_add_success"] = False

    # Filter popover
    with cFilter:
        with st.popover("Filter", icon="🔎", use_container_width=True):    

            categories = category_model.get_categories()
            st.selectbox("📦 Category Name", options=categories, format_func=lambda c: c["name"], key="select_category2")

            bClear, bFilter = st.columns(2)

            if bClear.button("❌ Clear Filter", use_container_width=True):
                st.session_state.budget_filter_applied = False
                st.session_state.budget_filter_data = {}
                st.rerun()

            # Button filter
            if bFilter.button("🔎 Search", use_container_width=True):
                selected_category = st.session_state.get("select_category2")

                st.session_state.budget_filter_applied = True
                st.session_state.budget_filter_data = {
                    "category_id": selected_category["_id"] if selected_category else None
                }

                st.rerun()

def render_budgets_details(category_model: CategoryModel, analyzer_model: FinanceAnalyzer, budget_model: BudgetModel, budget_type: str, currency: str):

    with stylable_container(key=budget_type, css_styles=container_main_css()):

        # Show budgets if exists 
        total_budget_by_type = budget_model.get_budget_by_budget_type(budget_type)

        # APPLY CATEGORY FILTER (BUDGET)
        if st.session_state.get("budget_filter_applied"):
            f = st.session_state.get("budget_filter_data", {})
            if f.get("category_id"):
                total_budget_by_type = [
                    b for b in total_budget_by_type
                    if b["category_id"] == f["category_id"]
                ]

        if not total_budget_by_type:
            st.subheader("No budget found!")

        # Total budget
        _, _, min_value = get_format_currency(currency)
        total_budget = min_value
        for item in total_budget_by_type:
            total_budget += analyzer_model.normalize_amount_to_user_currency(item["amount"], item["currency"])

        total_budget = get_format_amount(currency, total_budget)

        st.write(f"Total budget: {len(total_budget_by_type)} — Total amount: {total_budget}")
        st.write("")

        # Loop through budgets
        for idi, budget in enumerate(total_budget_by_type):

            # Get budget info - get category name by id
            category_id = budget["category_id"]
            category_name = category_model.get_category_name_by_id(category_id)
            
            # Get category icon
            icon = category_model.get_category_by_id(category_id).get('icon')

            # Get budget info - month, year
            budget_month = budget["month"]
            budget_year = budget["year"]

            # Get budget info - other
            budget_type = budget["budget_type"]

            # Get budget info - amount and currency
            budget_amount_format = analyzer_model.format_amounth_currency_for_user(budget["amount"], budget["currency"])
            budget_amount = budget["amount"]
            budget_currency = budget["currency"]
            
            # Get budget spend by budget type
            if budget_type == "Monthly":
                budget_spend = analyzer_model.get_spent_for_month_by_category(category_id, budget_month, budget_year, budget_currency)
                budget_spend_format = analyzer_model.format_amounth_currency_for_user(budget_spend, budget_currency)
            else:
                budget_spend = analyzer_model.get_spent_for_year_by_category(category_id, budget_year, budget_currency)
                budget_spend_format = analyzer_model.format_amounth_currency_for_user(budget_spend, budget_currency)

            # Calculate percent for progress bar
            percent_complete = budget_spend / budget_amount
            percent = round(percent_complete * 100,2)

            # Don't allow percent > 100 (error cause progress bar), bỏ vì dùng bar giả từ html css
            #if percent_complete > 1:
            #   percent_complete = 1.0 # 1.0 để giữ thanh bar luôn đầy khi quá 100%
            st.write("") # đẩy xuống để cân bằng với line

            cLeft, cMid,cRight = st.columns([5, 1.5, 1])
            with cLeft.container():

                # Budget type
                if budget_type == "Monthly":
                    budget_month_name = get_month_name(budget_month)
                    st.write(f"{icon} {category_name} — {budget_month_name}/{budget_year}")
                else:
                    st.write(f"{icon} {category_name} — {budget_year}")

                # Percent & Exceeded
                render_budget_progress(percent_complete)
                if percent > 100:
                    st.write(f"‼️ Exceeded: {percent}%")
                elif percent > 70:
                    st.write(f"⚠️ Warning: {percent}%")
                else:
                    st.write(f"🟢 On track: {percent}%")

            with cMid.container():
                st.write(f"Budget: {budget_amount_format}")
                st.write(f"Spent: {budget_spend_format}")

            with cRight.container():
                st.write("")  # đẩy xuống
                cEdit, cDelete = st.columns(2)

                # EDIT BUDGET
                with cEdit.popover("✏️", use_container_width=True):
                    st.write("Edit budget")

                    # ---------- Keys ----------
                    key_cate = f"edit_budget_cate_{budget['_id']}"
                    key_type = f"edit_budget_type_{budget['_id']}"
                    key_currency = f"edit_budget_currency_{budget['_id']}"
                    key_amount = f"edit_budget_amount_{budget['_id']}"
                    key_month = f"edit_budget_month_{budget['_id']}"
                    key_year = f"edit_budget_year_{budget['_id']}"

                    col1, col2 = st.columns([1, 1])

                    # ---------- LEFT ----------
                    with col1:

                        # Category
                        cate_dict = category_model.get_categories()
                        cate_list = {c["name"]: c["_id"] for c in cate_dict}
                        cate_edit_options = cate_list.keys()

                        change_cate_name = st.selectbox(
                            "Change category",
                            options=cate_edit_options,
                            index=list(cate_list.values()).index(budget["category_id"]),
                            key=key_cate
                        )
                        change_cate_id = cate_list.get(change_cate_name)

                        # Amount
                        currencies_step, currencies_format, min_value = get_format_currency(budget["currency"])
                        change_amount = state_input(
                            label="Change amount",
                            current_data=budget["amount"],
                            widget=st.number_input,
                            key=key_amount,
                            min_value=min_value,
                            step=currencies_step,
                            format=currencies_format
                        )   

                        # Year
                        change_year = state_input(
                            label="Change year",
                            current_data=budget["year"],
                            widget=st.number_input,
                            key=key_year,
                            min_value=datetime.now().year - 2,
                            max_value=datetime.now().year + 2
                        )

                    # ---------- RIGHT ----------
                    with col2:

                        # Budget type
                        change_budget_type = st.selectbox(
                            "Change budget type",
                            options=["Monthly", "Yearly"],
                            index=["Monthly", "Yearly"].index(budget["budget_type"]),
                            key=key_type
                        )
                        
                        # Currency
                        change_currency = state_input(
                            label="Change currency",
                            current_data=budget["currency"],
                            widget=st.selectbox,
                            key=key_currency,
                            options=get_currencies_list()
                        )

                        # Month
                        if budget["budget_type"] == "Monthly":
                            change_month = state_input(
                                label="Change month",
                                current_data=budget["month"],
                                widget=st.number_input,
                                key=key_month,
                                min_value=1,
                                max_value=12
                            )

                    # ---------- SAVE ----------
                    if st.button("✅ Save", key=f"edit_budget_btn_{budget['_id']}", width="stretch"):
                        if (
                            change_amount == budget["amount"]
                            and change_currency == budget["currency"]
                            and change_cate_id == budget["category_id"]
                            and change_budget_type == budget["budget_type"]
                            and change_month == budget["month"]
                            and change_year == budget["year"]
                        ):
                            st.error("No changes were made.")
                        else:
                            if change_budget_type == "Yearly":
                                change_month = None

                            budget_model.save_budget(
                                budget["_id"],
                                category_id=change_cate_id,
                                budget_type=change_budget_type,
                                currency=change_currency,
                                amount=change_amount,
                                month=change_month,
                                year=change_year
                            )
                            st.session_state[f"edit_budget_success_{budget['_id']}"] = True
                            st.rerun()

                    # SUCCESS MESSAGE
                    if st.session_state.get(f"edit_budget_success_{budget['_id']}"):
                        st.success("Budget updated successfully!")
                        st.session_state[f"edit_budget_success_{budget['_id']}"] = False

                # DELETE BUDGET
                with cDelete:
                    if st.button("🗑️", key=f"delete_budget_{budget['_id']}", width="stretch"):
                        dialog_title = f"{category_name} ({budget_month}/{budget_year})" if budget_type == "Monthly" else f"{category_name} ({budget_year})"
                        delete_budget_id = budget["_id"]

                        @st.dialog(f"Are you sure you want to delete budget {dialog_title}?")
                        def confirm_delete_dialog():
                            cCancel, cConfirm = st.columns(2)

                            if cCancel.button("❌ Cancel", use_container_width=True):
                                st.rerun()

                            if cConfirm.button("✅ Confirm", use_container_width=True):
                                if budget_model.delete_budget(delete_budget_id):
                                    st.success("Budget deleted successfully!")
                                else:
                                    st.error("Failed to delete budget!")
                                st.rerun()

                        confirm_delete_dialog()

            if idi < len(total_budget_by_type) - 1: # ko in line dòng cuối                   
                st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)        

def render_budgets(analyzer_model: FinanceAnalyzer):
    models = st.session_state["models"]
    category_model = models["category"]
    budget_model = models["budget"]
    user_model = models["user"]
    default_currency = user_model.get_default_currency(st.session_state["user_id"])

    with stylable_container(key="budget_page_box", css_styles=container_page_css()):

        # Header
        cHeader, cFunc = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Budgets")
        with cFunc:
            render_budgets_func_panel(category_model, budget_model)

        # Line
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

        # Main
        tMonthly, tYearly = st.tabs(["Monthly", "Yearly"])
        with tMonthly:
            render_budgets_details(category_model, analyzer_model, budget_model, "Monthly", default_currency)
        with tYearly:
            render_budgets_details(category_model, analyzer_model, budget_model, "Yearly", default_currency)