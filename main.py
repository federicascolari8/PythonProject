""" Main script to exemplify the use of Sediment Analyst

This script contains the step-by-step process...
It should be clean, short, and tell a "story" of the
functionality of the entire code

Functions:
----
* first_function: ...


"""
# from config import *
from statistical_analyzer import StatisticalAnalyzer
from utils import *


def main():
    # initiate dataframe to hold all the  the samples statistics
    df_global = pd.DataFrame()

    # TODO Part1
    # loop through all the samples and compute corresponding
    # for i, file_name in enumerate(find_files(input["folder_path"])):

    # extract the sieving table from excel or csv
    sieving_df, metadata = extract_df(dic=input, file=sieving_data_add)

    # call the class StatisticalAnalyzer
    analyzer = StatisticalAnalyzer(sieving_df=sieving_df, metadata=metadata)
    print(analyzer.sampledate, analyzer.samplename, analyzer.coords)

    # TODO Part2
    # call the static plotter
    # plotter = StaticPlotter(analyzer)

        # TODO Part1 (inside of loop)
        # append global dataframe
        # df_global = append_global(obj=analyzer,
        #                          df=df_global,
        #                          file=file_name)

    pass


if __name__ == "__main__":
    # Call main function
    main()
