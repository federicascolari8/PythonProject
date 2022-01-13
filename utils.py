""" this module contains auxiliary functions to main

Functions:
----

"""
from config import *


def extract_df(dic=input):
    df = pd.read_excel(sieving_data_add,
                       header=dic["header"],
                       usecols=[dic["gs_clm"], dic["cw_clm"]],
                       nrows=dic["n_rows"],
                       engine="openpyxl"
                       )
    df.rename(columns={df.columns[0]: "Grain Sizes [mm]", df.columns[1]: "Fraction Mass [g]"},
              inplace=True)
    return df
