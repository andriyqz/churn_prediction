import os
import pandas as pd
import requests
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('PREDICT_API_URL', 'http://localhost:8000/predict_batch')

st.set_page_config(page_title="Churn Prediction", page_icon="📊", layout="wide")
st.title("Customer Churn")

st.subheader("Enter customer data")

col1, col2, col3 = st.columns(3)

with col1:
    customer_id = st.text_input("Customer ID", value="CUST-1001")
    tenure = st.number_input("Tenure (months)", min_value=0, value=12)
    warehouse_to_home = st.number_input(
        "Warehouse To Home", min_value=0, value=6
    )
    devices = st.number_input(
        "NumberOfDeviceRegistered", min_value=1, value=3
    )

with col2:
    prefered_cat = st.selectbox(
        "PreferedOrderCat",
        [
            "Laptop & Accessory",
            "Mobile Phone",
            "Fashion",
            "Grocery",
            "Others",
        ],
    )
    satisfaction = st.slider(
        "SatisfactionScore", min_value=1, max_value=5, value=3
    )
    marital_status = st.selectbox(
        "MaritalStatus", ["Single", "Married", "Divorced"]
    )
    addresses = st.number_input("NumberOfAddress", min_value=1, value=2)

with col3:
    complain = st.selectbox(
        "Complain", [0, 1], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)"
    )
    days_since_last_order = st.number_input(
        "DaySinceLastOrder", min_value=0, value=4
    )
    cashback = st.number_input("CashbackAmount", min_value=0.0, value=150.0)

if st.button("Predict", type="primary"):
    payload = [
        {
            "customer_id": customer_id,
            "Tenure": tenure,
            "WarehouseToHome": warehouse_to_home,
            "NumberOfDeviceRegistered": devices,
            "PreferedOrderCat": prefered_cat,
            "SatisfactionScore": satisfaction,
            "MaritalStatus": marital_status,
            "NumberOfAddress": addresses,
            "Complain": complain,
            "DaySinceLastOrder": days_since_last_order,
            "CashbackAmount": cashback,
        }
    ]

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            results = response.json().get("predictions", [])
            st.success("Prediction retrieved successfully!")
            st.dataframe(pd.DataFrame(results))
        else:
            st.error(
                f"API Error ({response.status_code}): {response.text}"
            )
    except Exception as e:
        st.error(f"Failed to connect to API server: {e}")