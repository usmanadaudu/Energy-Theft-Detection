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

    return cumm_usage_anomaly, detailed_cumm_usage_anomaly