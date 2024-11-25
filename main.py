import numpy as np
import pandas as pd
import streamlit as st

from utils import check_anomaly
from utils import get_tariff_rate
from utils import get_expected_units
from utils import get_anomalies_download_df


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
    accept_multiple_files=False,
    key="vending_data",
    help="Upload an excel file containing total amount customers pais per month as well as total amount of units credited per month"
)

if vending_data is not None:
    vending_df = pd.read_excel(vending_data)
    
    try:
        assert "CONS_NO" in vending_df.columns
        assert "MADE_NO" in vending_df.columns
        assert "Band" in vending_df.columns
        assert "May Kwh" in vending_df.columns
        assert "May Naira" in vending_df.columns
        assert "June Kwh" in vending_df.columns
        assert "June Naira" in vending_df.columns
        assert "July Kwh" in vending_df.columns
        assert "July Naira" in vending_df.columns
        assert "Aug Kwh" in vending_df.columns
        assert "Aug Naira" in vending_df.columns
        assert "Sept Kwh" in vending_df.columns
        assert "Sept Naira" in vending_df.columns
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

    st.write("Vending Data with Tariff Rate")
    st.write(vending_df.head())

    month_list = ["May", "June", "July", "Aug", "Sept"]

    expected_df = get_expected_units(vending_df, month_list)

    st.write("Expected Credit Units")
    st.write(expected_df.head())

    anomaly_df = check_anomaly(expected_df, month_list)

    st.write("Anomalies in Energy Purchase")
    st.write(anomaly_df)

    anomaly_file = get_anomalies_download_df(anomaly_df)

    @st.cache_data
    def download_anomalies_data(df):
        return df.to_excel(index=False).encode("utf-8")
    
    anomaly_download_file = download_anomalies_data(anomaly_file)

    st.download_button(
        "Download Payment Anomaly Data",
        anomaly_download_file,
        "Payment Anomalies.xlsx",
        mime="application/vnd.ms-excel",
        help="Click this button to download data of anomaly occurrences in units credited to customers as an excel file"
    )