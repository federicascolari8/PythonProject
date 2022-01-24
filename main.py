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
from static_plotter import StaticPlotter
from utils import *




def main():
    # initiate dataframe to hold all the  the samples statistics
    df_global = pd.DataFrame()

    # loop through all the samples and compute corresponding
    for i, file_name in enumerate(find_files(input["folder_path"])):
        # extract the sieving table from excel or csv
        sieving_df, metadata = extract_df(dic=input, file=file_name)

        # call the class StatisticalAnalyzer
        analyzer = StatisticalAnalyzer(sieving_df=sieving_df, metadata=metadata)
        # print(analyzer.sampledate, analyzer.samplename, analyzer.coords)


        # append global dataframe
        df_global = append_global(obj=analyzer,
                                  df=df_global
                                   )

        # call the class StaticPlotter
        plotter = StaticPlotter(analyzer)

        # plot the cumulative grain size distribution curve
        plotter.cum_plotter(file_name + ".png")

    print_excel(df=df_global)


    pass


if __name__ == "__main__":
    # Call main function
    main()
