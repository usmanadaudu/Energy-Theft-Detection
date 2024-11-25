def get_tariff_rate(band):
    """
    This function returns the tariff rate based on the band
    """
    # import numpy as np
    
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

