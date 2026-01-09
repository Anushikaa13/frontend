import streamlit as st
import pandas as pd
import logging

from config import PAGE_TITLE, LAYOUT, CACHE_TTL, API_BASE_URL
import api_client
from custom_components import (
    local_storage_get, local_storage_set, custom_metric_card,
    product_card, storage_info_widget
)
from advanced_charts import multi_chart_dashboard
from geospatial import (
    create_warehouse_map, create_product_distribution_map,
    create_supply_chain_map, location_based_inventory
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#----------------------Advanced Features: Day 9 Enhanced App----------------------------------------#
st.set_page_config(page_title=PAGE_TITLE, layout=LAYOUT)
logger.info(f"App initialized - API Base URL: {API_BASE_URL}")

# =========================
# CUSTOM THEME & SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 🎯 Product Management Pro")
    st.markdown("---")
    
    # Check browser storage for saved preferences
    theme_options = ["Light", "Dark"]
    saved_theme = local_storage_get("theme", "Light")
    
    # Ensure saved_theme is a valid option
    if saved_theme not in theme_options:
        saved_theme = "Light"
    
    theme_choice = st.radio(
        "Theme",
        theme_options,
        index=theme_options.index(saved_theme)
    )
    
    if theme_choice != saved_theme:
        local_storage_set("theme", theme_choice)

# =========================
# SESSION STATE
# =========================
if "token" not in st.session_state:
    st.session_state.token = local_storage_get("auth_token")

if "favorites" not in st.session_state:
    st.session_state.favorites = local_storage_get("favorites", [])

# =========================
# AUTH UI WITH STORAGE
# =========================
st.sidebar.title("🔐 Authentication")

auth_mode = st.sidebar.radio("Choose", ["Login", "Signup"])

username = st.sidebar.text_input("Username", key="username_input")
password = st.sidebar.text_input("Password", type="password", key="password_input")

if auth_mode == "Signup":
    if st.sidebar.button("✨ Create Account"):
        logger.info(f"Signup button clicked for user: {username}")
        res = api_client.signup(username, password)
        if res.status_code == 200:
            logger.info(f"Signup successful for user: {username}")
            st.sidebar.success("✅ User created. Please login.")
        else:
            logger.warning(f"Signup failed for user {username}: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", "Signup failed")
            except Exception as e:
                error_msg = res.text if res.text else f"Signup failed (HTTP {res.status_code})"
            st.sidebar.error(f"❌ {error_msg}")

if auth_mode == "Login":
    if st.sidebar.button("🚀 Login"):
        logger.info(f"Login button clicked for user: {username}")
        res = api_client.login(username, password)
        if res.status_code == 200:
            token = res.json()["access_token"]
            st.session_state.token = token
            local_storage_set("auth_token", token)  # Store in browser storage
            logger.info(f"Login successful for user: {username}")
            st.sidebar.success("✅ Logged in successfully")
            st.rerun()
        else:
            logger.warning(f"Login failed for user {username}: Status {res.status_code}")
            try:
                error_msg = res.json().get("detail", "Login failed")
            except Exception as e:
                error_msg = res.text if res.text else "Invalid credentials"
            st.sidebar.error(f"❌ {error_msg}")

# Show logout button if logged in
if st.session_state.token:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.token = None
        local_storage_set("auth_token", None)
        st.rerun()

# Display storage info
storage_info_widget()

# =========================
# MAIN APP
# =========================
st.title("🏭 Product Management Pro")
st.markdown("*Advanced Analytics & Geospatial Intelligence*")

if not st.session_state.token:
    st.warning("⚠️ Please login to continue.")
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
# NAVIGATION TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Products",
    "📊 Analytics",
    "🗺️ Geospatial",
    "⚙️ Manage",
    "💾 Storage"
])

# ========================= TAB 1: PRODUCTS =========================
with tab1:
    st.subheader("📦 Product Catalog")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Add New Product")
        with st.form("add_product"):
            name = st.text_input("Product Name")
            description = st.text_input("Description")
            price = st.number_input("Price ($)", min_value=0.0, format="%.2f")
            quantity = st.number_input("Quantity (units)", min_value=0, step=1)

            submitted = st.form_submit_button("✅ Add Product")

            if submitted:
                logger.info(f"Add product form submitted: {name}, price: {price}")
                res = api_client.create_product(st.session_state.token, name, description, price, quantity)

                if res.status_code == 200:
                    logger.info(f"Product added successfully: {name}")
                    st.success("✅ Product added successfully")
                    fetch_products.clear()
                    st.rerun()
                else:
                    logger.error(f"Failed to add product: Status {res.status_code}")
                    try:
                        error_msg = res.json().get("detail", res.text)
                    except:
                        error_msg = res.text or f"Error: {res.status_code}"
                    st.error(f"❌ {error_msg}")
    
    with col2:
        if st.button("🔄 Refresh"):
            fetch_products.clear()
            st.rerun()
    
    st.markdown("---")
    
    # =========================
    # FILTERS
    # =========================
    st.markdown("### 🔍 Filter & Sort")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_price = st.number_input("Min Price ($)", value=0.0)
    
    with col2:
        max_price = st.number_input("Max Price ($)", value=100000.0)
    
    with col3:
        sort_by = st.selectbox("Sort By", ["price", "quantity", "name"])
    
    with col4:
        sort_order = st.selectbox("Order", ["asc", "desc"])
    
    # =========================
    # PAGINATION
    # =========================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        page_size = st.selectbox("Items per page", [10, 20, 50, 100])
    
    with col2:
        page = st.number_input("Page", min_value=0, step=1)
    
    # =========================
    # FETCH & DISPLAY PRODUCTS
    # =========================
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
        token=token
    )
    
    if not products:
        st.info("No products found")
    else:
        # Display as cards
        st.markdown("### 🛍️ Products")
        cols = st.columns(2)
        
        for idx, product in enumerate(products):
            with cols[idx % 2]:
                product_card(product)
                
                # Add to favorites button
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("❤️ Favorite", key=f"fav_{product.get('id')}"):
                        if product.get('id') not in st.session_state.favorites:
                            st.session_state.favorites.append(product.get('id'))
                            local_storage_set("favorites", st.session_state.favorites)
                            st.success("Added to favorites!")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{product.get('id')}"):
                        logger.info(f"Delete product button clicked for ID: {product.get('id')}")
                        res = api_client.delete_product(token, product.get('id'))
                        if res.status_code == 200:
                            logger.info(f"Product deleted: ID {product.get('id')}")
                            st.success("Product deleted!")
                            fetch_products.clear()
                            st.rerun()
                        else:
                            st.error("Failed to delete")

# ========================= TAB 2: ANALYTICS =========================
with tab2:
    st.subheader("📊 Advanced Analytics")
    
    if not products:
        st.info("No products to analyze")
    else:
        df = pd.DataFrame(products)
        multi_chart_dashboard(df)

# ========================= TAB 3: GEOSPATIAL =========================
with tab3:
    st.subheader("🗺️ Geospatial Intelligence")
    
    geo_tab1, geo_tab2, geo_tab3, geo_tab4 = st.tabs([
        "🏭 Warehouses",
        "📍 Distribution",
        "⛓️ Supply Chain",
        "📦 Inventory Map"
    ])
    
    with geo_tab1:
        st.markdown("### Warehouse Network")
        create_warehouse_map(products)
    
    with geo_tab2:
        st.markdown("### Product Distribution Heatmap")
        if products:
            create_product_distribution_map(pd.DataFrame(products))
    
    with geo_tab3:
        st.markdown("### Supply Chain Network")
        create_supply_chain_map()
    
    with geo_tab4:
        st.markdown("### Location-Based Inventory")
        location_based_inventory()

# ========================= TAB 4: MANAGE =========================
with tab4:
    st.subheader("⚙️ Product Management")
    
    manage_tab1, manage_tab2 = st.tabs(["📋 List", "✏️ Bulk Actions"])
    
    with manage_tab1:
        st.markdown("### All Products")
        if products:
            df = pd.DataFrame(products)
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="products.csv",
                mime="text/csv"
            )
    
    with manage_tab2:
        st.markdown("### Bulk Operations")
        
        if st.button("📊 Export All Data"):
            if products:
                df = pd.DataFrame(products)
                st.json(df.to_dict('records'))
        
        if st.button("🔄 Sync with Storage"):
            local_storage_set("products", products)
            st.success("✅ Data synced to browser storage!")

# ========================= TAB 5: STORAGE =========================
with tab5:
    st.subheader("💾 Browser Storage Management")
    
    st.markdown("### Stored Data")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Auth Token:**")
        st.code(st.session_state.token[:20] + "..." if st.session_state.token else "None")
    
    with col2:
        st.markdown("**Favorites:**")
        st.write(st.session_state.favorites)
    
    st.markdown("---")
    
    st.markdown("### Storage Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear All Storage"):
            st.session_state.favorites = []
            local_storage_set("auth_token", None)
            local_storage_set("favorites", [])
            st.success("✅ Storage cleared!")
    
    with col2:
        if st.button("📦 Cache Products"):
            if products:
                local_storage_set("cached_products", products)
                st.success("✅ Products cached!")
    
    with col3:
        if st.button("📊 View Storage Stats"):
            st.json({
                "token_stored": bool(st.session_state.token),
                "favorites_count": len(st.session_state.favorites),
                "theme": local_storage_get("theme", "Light")
            })

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    <p>🚀 Product Management Pro | Advanced Analytics Dashboard</p>
    <p>API: {api_base_url} | Streamlit v{st.__version__}</p>
</div>
""".format(api_base_url=API_BASE_URL, st=st), unsafe_allow_html=True)


