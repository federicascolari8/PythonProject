""" This module contains all the imported packages (dependencies) and
user inputs.
"""

try:
    import numpy as np
    import scipy
    from pathlib import Path
    from matplotlib import pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    import pandas as pd
    import openpyxl
    import matplotlib.ticker as mtick
    import seaborn as sns
    import re
    import locale
    import logging
    from pathlib import Path
    import glob
    import sys
    import os
except:
    print(
        "Error importing necessary packages. Required packages")

# Dataset path
# sieving_data_add = Path(os.path.abspath(os.getcwd()) + "/datasets/KB08_FC_1-2_nachher.xlsx")
sieving_data_add = "datasets/KB08_FC_1-2_nachher.xlsx"

# head and columns of the Grain Size (GS) and Class Weight (CW)


input = {"sample_name": None,
         "header": 8,
         "gs_clm": 1,  # grain size column index (start with 0)
         "cw_clm": 2,  # class weight column index (start with 0)
         "n_rows": 16,  # number of rows (available class weights)
         "porosity": 0.1778,  # option to give porosity manually
         "SF_porosity": 6.10, # default for rounded sediment
         "coordinates": None  # coordinates of the sample (tuple variable)
         }
