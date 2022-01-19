""" This module contains auxiliary functions to main

Functions:
----

"""
from config import *


def extract_df(dic=input, file=None):
    """

    :param dic: global input parameters that can be altered in the config.py file
    :param file: str: name of the file containing a sieving sample
    :return: dataframe of sieving sample
    """
    df = pd.read_excel(file, engine="openpyxl", header=None)
    dff = df.copy()
    columns_to_get = [dic["gs_clm"], dic["cw_clm"]]
    dff_gs = dff.iloc[dic["header"]: dic["header"] + dic["n_rows"], columns_to_get]
    dff_gs.reset_index(inplace=True, drop=True)
    dff_gs = dff_gs.astype(float)

    # Get metadata from the dataframe
    # get sample name
    try:
        samplename = dff.iat[dic["index_sample_name"][0], dic["index_sample_name"][1]]
    except Exception as e:
        logging.error("Index for sample name not recognized, "
                      "assigning None to the sample name.")
        samplename = None
        print(e)
        pass

    # get sample date
    try:
        sampledate = dff.iat[dic["index_sample_date"][0], dic["index_sample_date"][1]]
    except Exception as e:
        logging.error("Index for sample date not recognized, "
                      "assigning None to the sample date.")
        sampledate = None
        print(e)
        pass

    # get sample coordinates
    try:
        lat = dff.iat[dic["index_lat"][0], dic["index_lat"][1]]
        long = dff.iat[dic["index_long"][0], dic["index_long"][1]]
    except Exception as e:
        logging.error("Index for latitude and longitude not recognized, "
                      "assigning None to both latitude and longitude.")
        lat, long = None, None
        print(e)
        pass

    metadata = [samplename, sampledate, (lat, long)]

    # Rename and standardize the Grain Size dataframe
    dff_gs.rename(columns={dff_gs.columns[0]: "Grain Sizes [mm]", dff_gs.columns[1]: "Fraction Mass [g]"},
                  inplace=True)
    return dff_gs, metadata


def find_files(folder=None):
    """lists the file names in the folder that contains
    the samples

    :param folder: string of folder's address
    :return: list of strings from addresses of all files inside the folder
    """

    # Append / or / in director name if it does not have
    if not str(folder).endswith("/") and not str(folder).endswith("\\"):
        folder = Path(str(folder) + "/")

    # Create a list of shape files or raster files names
    file_list = glob.glob(str(folder) + "/*.xlsx")

    return file_list


def append_global(obj=None, df=None, file=None):
    """ A function to append all information stemming from the class
    Statistical Analyzer into one dataframe for further filtering and analyses
    :param obj: object of the class StatisticalAnalyzer
    :param df: df to be appended
    :param file: str :name of the sample file
    :return: Appended dataframe with statistics of sample file
    """

    # organize statistics to append in global df
    df_stat = pd.DataFrame()
    df_stat = df_stat.append(obj.statistics_df.transpose())
    df_stat.columns = df_stat.iloc[0]
    df_stat.drop("Name", axis=0, inplace=True)
    df_stat.reset_index(drop=True, inplace=True)

    # extract name and date of the sample
    df_name_date = pd.read_excel(file, engine="openpyxl")
    sample_name = df_name_date.at[input["index_sample_name"][0] - 2,
                                  df_name_date.columns[input["index_sample_name"][1] - 1]]
    sample_date = df_name_date.at[input["index_sample_date"][0] - 2,
                                  df_name_date.columns[input["index_sample_date"][1] - 1]]

    # organize porosity and conductivity to append in global df
    list_name = obj.porosity_conductivity_df["Name"].to_list()
    list_name_new = []
    for name in list_name:
        list_name_new.append("{} [Porosity]".format(name))
        list_name_new.append("{} [Estimated kf]".format(name))

    df_temp = pd.DataFrame(columns=list_name_new)
    new_row = obj.porosity_conductivity_df["Porosity"].to_list()
    new_row = new_row + obj.porosity_conductivity_df["Corresponding kf [m/s]"].to_list()
    df_temp.loc[0] = new_row

    # join df_stat and df_poro_cond
    df_add = pd.concat([df_stat, df_temp], axis=1)

    if df.empty:
        d = 1  # append the first dataframe with columns names
    else:
        d = 3  # append only values of the new file

    pass
