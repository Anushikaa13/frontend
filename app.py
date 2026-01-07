import streamlit as st
import pandas as pd
import logging

from config import PAGE_TITLE, LAYOUT, CACHE_TTL, API_BASE_URL
import api_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#----------------------Day 7 + Day 8 tasks----------------------------------------#
st.set_page_config(page_title=PAGE_TITLE, layout=LAYOUT)
logger.info(f"App initialized - API Base URL: {API_BASE_URL}")

# =========================
# SESSION STATE
# =========================
if "token" not in st.session_state:
    st.session_state.token = None

# =========================
# AUTH UI
# =========================
st.sidebar.title("Authentication")

auth_mode = st.sidebar.radio("Choose", ["Login", "Signup"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if auth_mode == "Signup":
    if st.sidebar.button("Create Account"):
        logger.info(f"Signup button clicked for user: {username}")
        res = api_client.signup(username, password)
        if res.status_code == 200:
            logger.info(f"Signup successful for user: {username}")
            st.sidebar.success("User created. Please login.")
        else:
            logger.warning(f"Signup failed for user {username}: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", "Signup failed")
            except Exception as e:
                error_msg = res.text if res.text else f"Signup failed (HTTP {res.status_code})"
            st.sidebar.error(error_msg)

if auth_mode == "Login":
    if st.sidebar.button("Login"):
        logger.info(f"Login button clicked for user: {username}")
        res = api_client.login(username, password)
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            logger.info(f"Login successful for user: {username}")
            st.sidebar.success("Logged in successfully")
        else:
            logger.warning(f"Login failed for user {username}: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", "Login failed")
            except Exception as e:
                error_msg = res.text if res.text else "Invalid credentials"
            st.sidebar.error(error_msg)

# =========================
# MAIN APP
# =========================
st.title("Product Management System")

if not st.session_state.token:
    st.warning("Please login to continue.")
    st.stop()

# =========================
# FETCH PRODUCTS function
# =========================
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_products(
min_price,
max_price,
sort_by,
sort_order,
skip,
limit,
token
):
 return api_client.fetch_products(
     token,
     min_price,
     max_price,
     sort_by,
     sort_order,
     skip,
     limit
 )
# =========================
# CREATE PRODUCT
# =========================
st.subheader("➕ Add New Product")

with st.form("add_product"):
    name = st.text_input("Name")
    description = st.text_input("Description")
    price = st.number_input("Price", min_value=0.0)
    quantity = st.number_input("Quantity", min_value=0, step=1)

    submitted = st.form_submit_button("Add Product")

    if submitted:
        logger.info(f"Add product form submitted: {name}, price: {price}")
        res = api_client.create_product(st.session_state.token, name, description, price, quantity)

        if res.status_code == 200:
            logger.info(f"Product added successfully: {name}")
            st.success("Product added successfully")
            fetch_products.clear()   # clear cache
            st.rerun()                # refresh UI

        else:
            logger.error(f"Failed to add product: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", res.text)
            except:
                error_msg = res.text or f"Error: {res.status_code}"
            st.error(error_msg)

# =========================
# FILTERS
# =========================
st.subheader(" Filter & Sort Products")

col1, col2, col3 = st.columns(3)

with col1:
    min_price = st.number_input("Min Price", value=0.0)

with col2:
    max_price = st.number_input("Max Price", value=100000.0)

with col3:
    sort_by = st.selectbox("Sort By", ["price", "quantity", "name"])

sort_order = st.radio("Sort Order", ["asc", "desc"])

# =========================
# FETCH PRODUCTS
# =========================

page_size = st.selectbox("Items per page", [10, 20, 50])
page = st.number_input("Page", min_value=0, step=1)

token = st.session_state.token

if token is None:
    st.warning("Please log in first.")
    st.stop()

products = fetch_products(
min_price=min_price,
max_price=max_price,
sort_by=sort_by,
sort_order=sort_order,
skip=page * page_size,
limit=page_size,
token=st.session_state.token
)
df = pd.DataFrame(products)

# =========================
# DISPLAY PRODUCTS
# =========================
st.subheader("Products")

if df.empty:
    st.info("No products found.")
else:
    st.dataframe(df, use_container_width=True)

# =========================
# DELETE PRODUCT
# =========================
st.subheader("Delete Product")

if not df.empty:
    product_id = st.selectbox("Select Product ID", df["id"].tolist())

    if st.button("Delete"):
        logger.info(f"Delete product button clicked for ID: {product_id}")
        res = api_client.delete_product(st.session_state.token, product_id)
        if res.status_code == 200:
            logger.info(f"Product deleted successfully: ID {product_id}")
            st.success("Product deleted. Refresh page.")
            fetch_products.clear()
            st.rerun()
        else:
            logger.error(f"Failed to delete product ID {product_id}: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", res.text)
            except:
                error_msg = res.text or "Failed to delete"
            st.error(error_msg)

# =========================
# CHART
# =========================
st.subheader("Price Distribution")

if not df.empty:
    st.bar_chart(df.set_index("name")["price"])

if st.button("🔄 Refresh Products"):
    fetch_products.clear()
    st.rerun()

