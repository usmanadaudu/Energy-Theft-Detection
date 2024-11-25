import pandas as pd
import streamlit as st


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
    
st.write(vending_df.head())
    
