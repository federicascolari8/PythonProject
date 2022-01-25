import plotly.express as px
from config import *


class InteracPlotter:
    def __init__(self, df):
        self.df = df

    def plot_histogram(self, param):
        fig = px.histogram(self.df,
                           x=param,
                           labels={
                               param: str(param).capitalize(),  # capitalizes first letter of the parameter
                               #TODO: impl. label below
                               'count': 'Absolute Frequency [-]'
                           })

        return fig
