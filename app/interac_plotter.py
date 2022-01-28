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
                               # TODO: impl. label below
                               'count': 'Absolute Frequency [-]'
                           },
                           title="Histogram of Statistics")

        return fig

    def plot_gsd(self, samples):
        # filter samples given sample name
        df = self.df[self.df["sample name"].isin(samples)]

        # filter only grainsize, samples name and class weight
        df_gsd = df.set_index("sample name").iloc[:, 33:49].stack().reset_index()

        # rename columns for future reference
        df_gsd.rename(columns={df_gsd.columns[1]: "gsd", df_gsd.columns[2]: "cw"}, inplace=True)

        # create GSD figure
        fig = px.line(df_gsd, x="gsd", y="cw", color='sample name', title="Grain Size Distribution")
        fig.update_xaxes(type="log")

        return fig
