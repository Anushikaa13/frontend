# ======================================================
# Day 3: Streamlit Frontend with JWT Authentication
# ======================================================

import streamlit as st
import requests
import os

# BACKEND_URL = "http://127.0.0.1:8000" --local
#BACKEND_URL = "https://backend-1-f0fm.onrender.com"  # --remote
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.title("Product Management Login")

# ------------------------------------------------------
# Session State (stores token)
# ------------------------------------------------------
if "token" not in st.session_state:
    st.session_state.token = None

# ------------------------------------------------------
# LOGIN FORM
# ------------------------------------------------------
if st.session_state.token is None:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{BACKEND_URL}/token",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------------------------------------------
# PROTECTED SECTION
# ------------------------------------------------------
else:
    st.success("You are logged in")

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # --------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------
    st.subheader("Add Product")

    id = st.number_input("Product ID", step=1)
    name = st.text_input("Product Name")
    price = st.number_input("Price", step=0.5)
    quantity = st.number_input("Quantity", step=1)

    if st.button("Add Product"):
        product = {
            "id": int(id),
            "name": name,
            "price": float(price),
            "quantity": int(quantity)
        }

        res = requests.post(
            f"{BACKEND_URL}/products",
            json=product,
            headers=headers
        )

        if res.status_code == 200:
            st.success("Product added successfully")
        else:
            st.error("Token expired or unauthorized")

    # --------------------------------------------------
    # VIEW PRODUCTS
    # --------------------------------------------------
    st.subheader("Product List")

    res = requests.get(
        f"{BACKEND_URL}/products",
        headers=headers
    )

    if res.status_code == 200:
        st.json(res.json())
    else:
        st.error("Session expired. Please login again.")

    # --------------------------------------------------
    # LOGOUT
    # --------------------------------------------------
    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
