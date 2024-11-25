import numpy as np
import pandas as pd
import streamlit as st

from utils import check_anomaly
from utils import get_tariff_rate
from utils import get_expected_units
from utils import check_monthly_usage
from utils import check_cumm_usage_diff
from utils import get_anomalies_df_for_download


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

is_vending_data_uploaded = False
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
        
    # st.write(vending_df.head())
    try:
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

        # st.write("Vending Data with Tariff Rate")
        # st.write(vending_df.head())

        month_list = ["May", "June", "July", "Aug", "Sept"]

        expected_df = get_expected_units(vending_df, month_list)

        # st.write("Expected Credit Units")
        # st.write(expected_df.head())

        anomaly_df = check_anomaly(expected_df, month_list)

        st.write("**Anomalies in Energy Purchase**")
        st.write(anomaly_df)

        anomaly_file = get_anomalies_df_for_download(anomaly_df, month_list)

        # st.write("Anomalies for Download")
        # st.write(anomaly_file)

        @st.cache_data
        def download_anomalies_data(df):
            return df.to_csv(index=False).encode("utf-8")
        
        anomaly_download_file = download_anomalies_data(anomaly_file)

        # st.write(anomaly_download_file)

        st.download_button(
            label="Download Payment Anomaly Data",
            data=anomaly_download_file,
            file_name="Payment Anomalies.csv",
            mime="text/csv",
            help="Click this button to download data of anomaly occurrences in units credited to customers as a csv file"
        )

        is_vending_data_uploaded = True
    except Exception as e:
        st.error(e)


st.header("Detection of Cyber Attack on Cummulative Energy Usage")
st.write("For any meter, two reading are being taken. The first reading is the cummulative energy usage of customers")
st.write("This reading starts from when the meter is installed till the current time. This reading is asynchronously sent to power stations to monitor energy usage of customers")
st.write("Anytime the cummulative energy usage reading for a customer reduces, this is an indication of anomaly")

meter_data = st.file_uploader(
    "Upload All Customers Meter Data After Uploading Vending Data",
    type=["xls", "xlsx"],
    accept_multiple_files=True,
    key="meter_data",
    help="After uploading vending data, upload an excel file containing the cummulative energy usage and residual energy usage for all customers taken at the begining of every month",
    disabled= not is_vending_data_uploaded
)

if meter_data:

    meter_readings_df = pd.DataFrame()
    for uploaded_file in meter_data:
        dataset = pd.read_excel(uploaded_file, sheet_name=None)
        input_df = dataset[list(dataset.keys())[-1]]

        if "ENERGY(KWH)" in input_df.columns:
                input_df.rename(columns={"ENERGY(KWH)": "Energy Reading(kwh)"}, inplace=True)

        if "CONSUMPTION(KWH)" in input_df.columns:
            input_df.rename(columns={"CONSUMPTION(KWH)": "Meter Units(kwh)"}, inplace=True)

        if "Consumption(kwh)" in input_df.columns:
            input_df.rename(columns={"Consumption(kwh)": "Meter Units(kwh)"}, inplace=True)

        assert "Meter SN" in input_df.columns, "Each file should contain the column `Meter SN` which is the meter number"
        assert "Frozen Time" in input_df.columns, "Each file should contain the column `Frozen Time` which is the time the reading was recorded"
        assert "Energy Reading(kwh)" in input_df.columns, "Each file should contain the column `ENERGY(KWH)` or `Energy Reading(kwh)` which is the Cummulative energy reading"
        assert "Meter Units(kwh)" in input_df.columns, "Each file should contain the column `CONSUMPTION(KWH)` or `Consumption(kwh)` which is the residual units on the meter"

        input_df = input_df[["Meter SN", "Frozen Time", "Energy Reading(kwh)", "Meter Units(kwh)"]]

        if not meter_readings_df.shape[0]:
            meter_readings_df = input_df
        else:
            meter_readings_df = pd.concat([meter_readings_df, input_df], ignore_index=True)

    meter_readings_df["Frozen Time"] = pd.to_datetime(meter_readings_df["Frozen Time"])
    meter_readings_df["Month"] = meter_readings_df["Frozen Time"].dt.month_name()

    meter_readings_df.sort_values(by=["Meter SN", "Frozen Time"], inplace=True)
    meter_readings_df.reset_index(drop=True, inplace=True)

    st.write(meter_readings_df.head())

    cumm_usage_anomaly, detailed_cumm_usage_anomaly = check_cumm_usage_diff(meter_readings_df)

    st.write("**Cummulative Usage Anomalies**")
    st.write(cumm_usage_anomaly)

    st.write("**Detailed Cummulative Usage Anomaly**")
    st.write(detailed_cumm_usage_anomaly)

    @st.cache_data
    def download_cumm_anomalies_data(df):
        return df.to_csv(index=False).encode("utf-8")

    cumm_anomaly_download_file = download_cumm_anomalies_data(detailed_cumm_usage_anomaly)

    st.download_button(
        label="Download Detailed Cummulative Usage Anomaly Data",
        data=cumm_anomaly_download_file,
        file_name="Cummulative Usage Anomalies.csv",
        mime="text/csv",
        help="Click this button to download data of cummulative usage anomaly occurrences as a csv file"
        )
    
    st.header("Detection of Cyber Attack on Monthly Energy Usage")
    st.write("Sometimes customers may tamper with meters to increase the residual units left on their meters")
    st.write("This final step is to detect such acts")
    st.write("The monthly usage of customers is gotten from the difference of the cummulative energy usage")
    st.write("When the monthly usage of customers is subtracted from the sum of the energy units the customer has at the beginning of the month and the amount of units the customer is credited in that month, this should be the amount of units left at the beginning of the next month")
    st.write("Anything contrary to this should be flagged as an anomaly")
    
    monthly_usage_anomaly = check_monthly_usage(meter_readings_df, expected_df)

    # st.write(monthly_usage_anomaly)

    @st.cache_data
    def download_monthly_usage_anomalies_data(df):
        return df.to_csv(index=False).encode("utf-8")

    monthly_usage_anomaly_download_file = download_monthly_usage_anomalies_data(monthly_usage_anomaly)

    st.download_button(
        label="Download Monthly Usage Anomaly Data",
        data=cumm_anomaly_download_file,
        file_name="Monthly Usage Anomalies.csv",
        mime="text/csv",
        help="Click this button to download data of monthly usage anomaly occurrences as a csv file"
        )