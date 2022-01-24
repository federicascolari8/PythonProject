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
    # extract the sieving table from excel or csv
    sieving_df = extract_df(dic=input)

    # call the class StatisticalAnalyzer
    analyzer = StatisticalAnalyzer(sieving_df=sieving_df)

    # print statistics as excel
    analyzer.print_excel()

    # call the class StaticPlotter
    plotter = StaticPlotter(analyzer)

    # plot the cumulative grain size ditribution curve
    plotter.cum_plotter("cum_curve.png")
    pass


if __name__ == "__main__":
    # Call main function
    main()
