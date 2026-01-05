import streamlit as st
import requests
import pandas as pd

st.title("Student Dashboard")
API_URL = "http://127.0.0.1:8000/students"
response = requests.get(API_URL)

if response.status_code == 200:
    students = response.json()
    df = pd.DataFrame(students)
    st.subheader("List of Students")
    st.dataframe(df)

    st.subheader("Age chart")
    st.bar_chart(df.set_index('name')['age'])
else:
    st.error("Failed to fetch data from the API")
