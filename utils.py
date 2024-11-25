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

def get_expected_units(df):
    month_list = ["May", "June", "July", "Aug", "Sept"]
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

