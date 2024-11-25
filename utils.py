def get_tariff_rate(band):
    """
    This function returns the tariff rate based on the band
    """
    import numpy as np
    
    if band == "A":
        tariff_rate = 209.5
    elif band == "B":
        tariff_rate = 62.48
    elif band == "C":
        tariff_rate = 45.80
    elif band == "D":
        tariff_rate = 31.24
    elif band == "E":
        tariff_rate = 31.34
    else:
        tariff_rate = np.nan

    return tariff_rate

def get_expected_units(df, month_list):
    permissible_error = 5    # amount of allowable error in percentage
    output_df = df.copy()

    for month in month_list:
        month_payment_column_name = " ".join([month, "Naira"])

        expected_units_column_name_5_5 = " ".join(["Expected Units",month,
                                                   "(5.5 VAT)"])
        lower_bound_column_name_5_5 = " ".join(["Lower Bound", month,
                                                "(5.5 VAT)"])
        upper_bound_column_name_5_5 = " ".join(["Upper Bound", month,
                                                "(5.5 VAT)"])

        expected_units_column_name_7_5 = " ".join(["Expected Units",month,
                                                   "(7.5 VAT)"])
        lower_bound_column_name_7_5 = " ".join(["Lower Bound", month,
                                                "(7.5 VAT)"])
        upper_bound_column_name_7_5 = " ".join(["Upper Bound", month,
                                                "(7.5 VAT)"])

        vat_charge_7_5 = 0.075 * df[month_payment_column_name]
        expected_units_7_5 = ((df[month_payment_column_name] - vat_charge_7_5)
                            / df["TARIFF_RATE"])
        output_df[expected_units_column_name_7_5] = expected_units_7_5
        output_df[lower_bound_column_name_7_5] = ((1 - permissible_error/100)
                                              * output_df[expected_units_column_name_7_5])
        output_df[upper_bound_column_name_7_5] = ((1 + permissible_error/100)
                                              * output_df[expected_units_column_name_7_5])

        vat_charge_5_5 = 0.055 * df[month_payment_column_name]
        expected_units_5_5 = ((df[month_payment_column_name] - vat_charge_5_5)
                            / df["TARIFF_RATE"])
        output_df[expected_units_column_name_5_5] = expected_units_5_5
        output_df[lower_bound_column_name_5_5] = ((1 - permissible_error/100)
                                              * output_df[expected_units_column_name_5_5])
        output_df[upper_bound_column_name_5_5] = ((1 + permissible_error/100)
                                              * output_df[expected_units_column_name_5_5])

    return output_df

def check_anomaly(df, month_list):
    output_df = df.copy()
    output_df["Anomaly"] = False

    for month in month_list:
        assigned_units_column_name = " ".join([month, "Kwh"])

        expected_units_column_name_7_5 = " ".join(["Expected Units",month,
                                                   "(7.5 VAT)"])
        lower_bound_column_name_7_5 = " ".join(["Lower Bound", month,
                                                "(7.5 VAT)"])
        upper_bound_column_name_7_5 = " ".join(["Upper Bound", month,
                                                "(7.5 VAT)"])

        expected_units_column_name_5_5 = " ".join(["Expected Units",month,
                                                   "(5.5 VAT)"])
        lower_bound_column_name_5_5 = " ".join(["Lower Bound", month,
                                                "(5.5 VAT)"])
        upper_bound_column_name_5_5 = " ".join(["Upper Bound", month,
                                                "(5.5 VAT)"])

        anomaly_column_name_5_5 = " ".join([month, "Anomaly (5.5 VAT)"])
        output_df[anomaly_column_name_5_5] = ((output_df[assigned_units_column_name]
                                           < output_df[lower_bound_column_name_5_5])
                                          + (output_df[assigned_units_column_name]
                                             > output_df[upper_bound_column_name_5_5]))

        anomaly_column_name_7_5 = " ".join([month, "Anomaly (7.5 VAT)"])
        output_df[anomaly_column_name_7_5] = ((output_df[assigned_units_column_name]
                                           < output_df[lower_bound_column_name_7_5])
                                          + (output_df[assigned_units_column_name]
                                             > output_df[upper_bound_column_name_7_5]))

        output_df["Anomaly"] = (
            output_df["Anomaly"]
            + (
                output_df[anomaly_column_name_5_5]
                * output_df[anomaly_column_name_7_5]
                )
            )

    return output_df

def get_anomalies_df_for_download(df, month_list):
    output_df = df.copy()
    output_column_names = ['CONS_NO', 'MADE_NO', 'Band','TARIFF_RATE']

    for month in month_list:
        output_column_names.append(" ".join([month, "Naira"]))
        output_column_names.append(" ".join([month, "Kwh"]))
        output_column_names.append(" ".join(["Expected Units", month,
                                             "(5.5 VAT)"]))
        output_column_names.append(" ".join(["Expected Units", month,
                                             "(7.5 VAT)"]))


    output_df = output_df.loc[output_df["Anomaly"], output_column_names]
    
    return output_df

def check_cumm_usage_diff(input_df):
    import pandas as pd

    assert "Meter SN" in input_df.columns, "Could not get meter number"
    assert "Frozen Time" in input_df.columns, "Could not get recording time"
    assert "Energy Reading(kwh)" in input_df.columns, "Could not get cummulative meter reading"

    cumm_usage_anomaly = pd.DataFrame()
    detailed_cumm_usage_anomaly = pd.DataFrame()

    for meter_no in input_df["Meter SN"].unique():
        df = input_df[input_df["Meter SN"] == meter_no].copy()

        df["Usage Diff"] = df["Energy Reading(kwh)"].diff()

        cumm_usage_anomaly_index = df[df["Usage Diff"] < 0].index

        if len(cumm_usage_anomaly_index):
            if not cumm_usage_anomaly.shape[0]:
                cumm_usage_anomaly = (df
                                      .loc[
                                          cumm_usage_anomaly_index,
                                           ["Meter SN", "Frozen Time"]
                                          ]
                                      )
                detailed_cumm_usage_anomaly = (df[df["Meter SN"] == meter_no])
            else:
                cumm_usage_anomaly = pd.concat(
                    [
                        cumm_usage_anomaly,
                        df.loc[cumm_usage_anomaly_index,["Meter SN", "Frozen Time"]]
                        ])
                detailed_cumm_usage_anomaly = pd.concat(
                    [
                        detailed_cumm_usage_anomaly,
                        df[df["Meter SN"] == meter_no]
                    ]
                )

    cumm_usage_anomaly.rename(
        columns={"Frozen Time": "Anomaly Occurence Date"}, 
        inplace=True
        )

    return cumm_usage_anomaly, detailed_cumm_usage_anomaly

def check_monthly_usage(input_df, expected_df):
    import pandas as pd

    assert "Meter SN" in input_df.columns, "Could not get meter number"
    assert "Frozen Time" in input_df.columns, "Could not get recording time"
    assert "Energy Reading(kwh)" in input_df.columns, "Could not get cummulative meter reading"
    assert "Meter Units(kwh)" in input_df.columns, "Could not get meter units data"

    input_df["Month Number"] = input_df["Frozen Time"].dt.month
    input_df.sort_values(by=["Meter SN", "Frozen Time"], inplace=True)
    input_df.reset_index(drop=True, inplace=True)

    monthly_usage_anomaly = pd.DataFrame()

    for meter_no in input_df["Meter SN"].unique():
        df = input_df[input_df["Meter SN"] == meter_no].copy()

        df["Energy Usage"] = -df["Energy Reading(kwh)"].diff(periods=-1)
        total_monthly_usage = df.groupby(by="Month")["Energy Usage"].sum()

        for month in df["Month"].unique():
            flag = False
            if month == "August":
                month_str = "Aug"
            elif month == "September":
                month_str = "Sept"
            else:
                month_str = month

            starting_units = (df
                              .loc[
                                  df["Month"] == month,
                                  "Energy Reading(kwh)"
                                  ].values[0])
            month_usage = total_monthly_usage[month]

            # the reading at the end of the current month is also the reading at
            # the start of the next month
            next_month_number = df["Month Number"].values[0] + 1
            try:
                ending_units = (df
                                .loc[
                                    df["Month Number"] == next_month_number,
                                    "Energy Reading(kwh)"
                                    ].values[0])
            except:
                flag = True
                continue

            units_bought = (expected_df
                            .loc[
                                expected_df["MADE_NO"]==meter_no,
                                " ".join([month_str, "Kwh"])
                                ]
                            )

            expected_ending_units = starting_units + units_bought.values[0] - month_usage
            if (units_bought.shape[0] and not flag):
                usage_anomaly = expected_ending_units != ending_units
                if usage_anomaly:
                    anomaly_data = {
                        "Meter SN": [meter_no],
                        "Month": [month],
                        "Staring Units": [starting_units],
                        "Energy Usage": [month_usage],
                        "Units Bought": [units_bought.values[0]],
                        "Expected Ending Units": [expected_ending_units],
                        "Ending Units": [ending_units]
                        }

                    if not monthly_usage_anomaly.shape[0]:
                        monthly_usage_anomaly = pd.DataFrame(anomaly_data)
                    else:
                        monthly_usage_anomaly = pd.concat(
                            [
                                monthly_usage_anomaly,
                                pd.DataFrame(anomaly_data)
                                ],
                            ignore_index=True
                            )

    return monthly_usage_anomaly