import streamlit as st
import requests
import pandas as pd

st.title("Product Management System")

API_URL = "http://127.0.0.1:8000/products"

#Add new product form
st.subheader("Add New Product")
with st.form(key='product_form'):
    id = st.number_input("Product ID", min_value=1, step=1)
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, format="%.2f" , step=0.5)
    quantity = st.number_input("Quantity", min_value=0, step=1)
    submit_button = st.form_submit_button('Add Product')

if submit_button:
    product_data = {
        "id": id,
        "name": name,
        "price": price,
        "quantity": quantity
    }
    response = requests.post(API_URL, json=product_data)
    print("Status code:", response.status_code)
    print("Headers:", response.headers)
    print("Raw text:", repr(response.text))

    if response.status_code == 200:
        st.success("Product added successfully!")
    else:
        st.error("Failed to add product.")

# Fetch and display products
response = requests.get(API_URL)
if response.ok:
    products = response.json()
    if products:
     df = pd.DataFrame(products)
     st.subheader("List of Products")
     st.dataframe(df)

     st.subheader("Price Chart")
     st.bar_chart(df.set_index('name')['price'])
    else:
      st.info("No products available.")
else:
    st.error("Failed to fetch data from the API")

# Delete product
st.subheader("Delete Product")
product_id_to_delete = st.number_input("Enter Product ID to delete", min_value=1, step=1, key='delete_id')
if st.button("Delete Product"):
    delete_url = f"{API_URL}/{product_id_to_delete}"
    delete_response = requests.delete(delete_url)
    if delete_response.status_code == 200:
        st.success("Product deleted successfully!")
    else:
        st.error("Failed to delete product.")

# Update product
st.subheader("Update Product")
product_id_to_update = st.number_input("Enter Product ID to update", min_value=1, step=1, key='update_id')
new_name = st.text_input("New Product Name", key='update_name')
new_price = st.number_input("New Price", min_value=0.0, format="%.2f", step=0.5, key='update_price')
new_quantity = st.number_input("New Quantity", min_value=0, step=1, key='update_quantity')  
if st.button("Update Product"):
    update_url = f"{API_URL}/{product_id_to_update}"
    updated_product_data = {
        "id": product_id_to_update,
        "name": new_name,
        "price": new_price,
        "quantity": new_quantity
    }
    update_response = requests.put(update_url, json=updated_product_data)
    if update_response.status_code == 200:
        st.success("Product updated successfully!")
    else:
        st.error("Failed to update product.")
