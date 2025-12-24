import streamlit as st
from models.user_model import UserModel
from models.category_model import CategoryModel
from models.transaction_model import TransactionModel
from models.budgets_model import BudgetModel
from utils import get_currencies_list
from assets.styles import container_page_css
from streamlit_extras.stylable_container import stylable_container

# ======== DiALOGS ========
# Confirm deactivate account dialog
@st.dialog("Are you sure you want to deactivate your account?", dismissible=False, width="small")
def confirm_deactivate_account_dialog(user_model: UserModel):
    st.write("Your account will be locked, but your data will remain stored. You can reactivate it by contacting support.")

    cCancel, cConfirm = st.columns([1, 1])
    if cCancel.button("❌ Cancel", use_container_width=True):
        st.rerun()

    if cConfirm.button("✅ Confirm", use_container_width=True):
        user_model.deactivate(st.session_state.user_id)
        st.rerun()

# Confirm delete account dialog
def confirm_delete_account_dialog(user_model: UserModel, category_model: CategoryModel, transaction_model: TransactionModel, budget_model: BudgetModel):
    user_id = st.session_state.user_id
    category_count = category_model.count_category_by_user(user_id)
    transaction_count = transaction_model.count_transaction_by_user(user_id)
    budget_count = budget_model.count_budget_by_user(user_id)

    # Check grammar
    category_count = f"{category_count} category" if category_count in [0, 1] else f"{category_count} categories"
    transaction_count = f"{transaction_count} transaction" if transaction_count in [0, 1] else f"{transaction_count} transactions"
    budget_count = f"{budget_count} budget" if budget_count in [0, 1] else f"{budget_count} budgets"

    # Check and show count dialog
    @st.dialog(f"Are you sure you want to delete your account?", dismissible=False, width="small")
    def _dialog(user_id):
        st.markdown(f"""
            Your data including:
            - {category_count}
            - {transaction_count}
            - {budget_count}
            """)
        st.write("When account is deleted, all your data will be permanently removed from our system. This action is irreversible.")
        st.write("")

        cCancel, cConfirm = st.columns([1, 1])
        if cCancel.button("❌ Cancel", use_container_width=True):
            st.rerun()

        if cConfirm.button("✅ Confirm", use_container_width=True):        
            # Delete account
            user_model.delete_user(user_id)
            st.session_state["setting_confirm_delete_message"] = True
            st.rerun()

    _dialog(user_id)

# Change currency success dialog
@st.dialog("Your default currency has been changed!", dismissible=False, width="small")
def change_currency_dialog():
    if st.button("✅ Close", use_container_width=True):
        st.rerun()
# ======== END DIALOGS ========

# ======== STREAMLIT RENDER =========
def render_dialog(user_model: UserModel, category_model, transaction_model, budget_model):
    if st.session_state.get("change_currency_success"):
        change_currency_dialog()
        st.session_state["change_currency_success"] = False

    if st.session_state.get("setting_confirm_deactivate"):
        confirm_deactivate_account_dialog(user_model)
        st.session_state["setting_confirm_deactivate"] = False

    if st.session_state.get("setting_confirm_delete"):
        confirm_delete_account_dialog(user_model, category_model, transaction_model, budget_model)
        st.session_state["setting_confirm_delete"] = False

def render_settings():
    models = st.session_state["models"]   # Lấy model từ App.py
    user_model = models["user"]
    category_model = models["category"]
    transaction_model = models["transaction"]
    budget_model = models["budget"]

    # Get user_currency from models
    user_currency = user_model.get_user_by_email(st.user.email).get("display_currency")

    with stylable_container(key="menu_box", css_styles=container_page_css()):

        # Header
        cHeader, _ = st.columns([1, 2], vertical_alignment="center")
        with cHeader:
            st.header("Settings")

        # Line
        st.markdown("""<hr style="margin: 10px 0; border: none; border-top: 2px solid #333; opacity: 0.3;">""", unsafe_allow_html=True)

        # Change currency
        st.subheader("Change Currency")
        cSelectBox, cButton = st.columns([3.4, 1], vertical_alignment="bottom")
        with cSelectBox:
            st.write("Transactions in other currencies will be automatically converted to your choosen default currency.")
            st.selectbox("Choose your default currency", get_currencies_list(), key="choose_currency", index=get_currencies_list().index(user_currency)) # Get current user currency
        with cButton:
            st.write("")
            if st.button("Save", use_container_width=True):
                if st.session_state["choose_currency"] == user_currency:
                    st.toast("You have not changed your currency.", duration=30) # during 30 seconds
                else:
                    user_model.update_display_currency(user_id=st.session_state["user_id"], currency=st.session_state["choose_currency"]) # Update user currency
                    st.session_state["change_currency_success"] = True
                    render_dialog(user_model, category_model, transaction_model, budget_model)

        st.divider()

        # Deactivate account
        st.subheader("Deactivate Account")
        cContent, cButton = st.columns([3.4, 1], vertical_alignment="bottom")
        with cContent:
            st.write("Deactivating your account will stop you from using our services, " \
            "but it will not remove your data from our system. You can reactivate it anytime by contacting Customer Support.")
        with cButton:
            if st.button("Deactivate Account", key="deactivate_account_button", use_container_width=True):
                st.session_state["setting_confirm_deactivate"] = True
                render_dialog(user_model, category_model, transaction_model, budget_model)
           
        st.divider()

        # Delete account
        st.subheader("Delete Account")
        cContent, cButton = st.columns([3.4, 1], vertical_alignment="bottom")
        with cContent:
            st.write("Permanently delete your account and all associated data. This action cannot be undone.")
        with cButton:
            if st.button("Delete Account", key="delete_account_button", use_container_width=True):
                st.session_state["setting_confirm_delete"] = True
                render_dialog(user_model, category_model, transaction_model, budget_model)

        st.divider()
# ======== END STREAMLIT RENDER ========