import numpy as np
import pandas as pd
import streamlit as st

from utils import get_tariff_rate


st.title("Detection of Energy Theft Through Cyber Attack")

st.write("This app implements a system for detecting energy theft which are orchestrated through cyber attack")

st.write("""
This app detects three types of cyber attacks

1. Cyber attack on energy unit purchases (getting more units than expected for amount paid)
2. Cyber attack on cummulative energy usage reading on meter
3. Cyber attck on meter residual units
""")

st.header("Detection of Cyber Attack on Energy Unit Purchases")
st.write("Sometimes consumers launch cyber attack on energy units purchase system in order to be given units far more than what they paid for")
st.write("These cyber attckas can be detected by comparing the total amount each customer pays per month with the total amount of units the customer is credited per month")
st.write("VAT is removed from any payment by customers before being credited with the amount left based on the band such customer is on. VAT was formerly 5.5% before being increased to 7.5%. The new VAT is not yet implemented for all customers. Therefore, a purchase will only be flagged if using any of the two VAT values leads to inconsistency in the amount of units credited")

vending_data = st.file_uploader(
    "Upload Customers Vending Data",
    type=["xls", "xlsx"],
    key="vending_data",
    help="Upload an excel file containing total amount customers pais per month as well as total amount of units credited per month"
)

if vending_data is not None:
    vending_df = pd.read_excel(vending_data)
    
try:
    assert "CONS_NO" in vending_data.columns
    assert "MADE_NO" in vending_data.columns
    assert "Band" in vending_data.columns
    assert "May Kwh" in vending_data.columns
    assert "May Naira" in vending_data.columns
    assert "June Kwh" in vending_data.columns
    assert "June Naira" in vending_data.columns
    assert "July Kwh" in vending_data.columns
    assert "July Naira" in vending_data.columns
    assert "Aug Kwh" in vending_data.columns
    assert "Aug Naira" in vending_data.columns
    assert "Sept Kwh" in vending_data.columns
    assert "Sept Naira" in vending_data.columns
except:
    st.error("Upload excel file having the following columns 'CONS_NO', 'MADE_NO', 'Band', 'May Kwh', 'May Naira', 'June Kwh', 'June Naira','July Kwh', 'July Naira', 'Aug Kwh', 'Aug Naira', 'Sept Kwh', 'Sept Naira'")
    
st.write(vending_df.head())

vending_df = vending_df[
    [
        "CONS_NO",
        "MADE_NO",
        "Band",
        "May Kwh",
        "May Naira",
        "June Kwh",
        "June Naira",
        "July Kwh",
        "July Naira",
        "Aug Kwh",
        "Aug Naira",
        "Sept Kwh",
        "Sept Naira"
    ]
]

vending_df["TARIFF_RATE"] = vending_df["Band"].apply(get_tariff_rate)

st.write(vending_df.head())