import streamlit as st
import requests
import pandas as pd

#----------------------Day 7 + Day 8 tasks----------------------------------------#
# =========================
# CONFIG
# =========================
BACKEND_URL = "https://backend-1-f0fm.onrender.com" # changed to deployed URL 

st.set_page_config(page_title="Product Management App", layout="wide")

# =========================
# SESSION STATE
# =========================
if "token" not in st.session_state:
    st.session_state.token = None

# =========================
# HELPERS
# =========================
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# =========================
# AUTH UI
# =========================
st.sidebar.title("Authentication")

auth_mode = st.sidebar.radio("Choose", ["Login", "Signup"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if auth_mode == "Signup":
    if st.sidebar.button("Create Account"):
        res = requests.post(
            f"{BACKEND_URL}/signup",
            json={"username": username, "password": password}
        )
        if res.status_code == 200:
            st.sidebar.success("User created. Please login.")
        else:
            st.sidebar.error(res.json()["detail"])

if auth_mode == "Login":
    if st.sidebar.button("Login"):
        res = requests.post(
            f"{BACKEND_URL}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.sidebar.success("Logged in successfully")
        else:
            st.sidebar.error("Invalid credentials")

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
@st.cache_data(ttl=60, show_spinner=False)
def fetch_products(
min_price,
max_price,
sort_by,
sort_order,
skip,
limit,
token
):
 params = {
 "min_price": min_price,
 "max_price": max_price,
 "sort_by": sort_by,
 "sort_order": sort_order,
 "skip": skip,
 "limit": limit
 }

 headers = {
 "Authorization": f"Bearer {token}"
 }

 res = requests.get(
 f"{BACKEND_URL}/products",
 params=params,
 headers=headers,
 timeout=5
 )

 res.raise_for_status()
 return res.json()
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
        res = requests.post(
            f"{BACKEND_URL}/products",
            json={
                "name": name,
                "description": description,
                "price": price,
                "quantity": quantity
            },
            headers=auth_headers()
        )

        if res.status_code == 200:
            st.success("Product added successfully")
            fetch_products.clear()   # clear cache
            st.rerun()                # refresh UI

        else:
            st.error(res.text)

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
        res = requests.delete(
            f"{BACKEND_URL}/products/{product_id}",
            headers=auth_headers()
        )
        if res.status_code == 200:
            st.success("Product deleted. Refresh page.")
            fetch_products.clear()
            st.rerun()
        else:
            st.error("Failed to delete")

# =========================
# CHART
# =========================
st.subheader("Price Distribution")

if not df.empty:
    st.bar_chart(df.set_index("name")["price"])

if st.button("🔄 Refresh Products"):
    fetch_products.clear()
    st.rerun()

