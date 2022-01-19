import pandas as pd
from config import *
import statistical_analyzer as sa


class StaticPlotter():
    def __init__(self, analyzer):
        self.df_cum = analyzer.cumulative_df
        print(self.df_cum)
