""" Module designated for the Interactive Plotter

Author : Federica Scolari

"""

from config import *
from app.appconfig import *


class InteractivePlotter:
    def __init__(self):
        self.df = pd.read_csv("overall_statistics.csv")

    def cum_gsd_plot(self):
        sample_names = self.df.iloc[:, 1].to_numpy().tolist()

        data = self.df.iloc[:, 34:50]
        grain_sizes = np.array(self.df.columns[34:50], dtype=float)
        ext_grain_sizes = []

        for i in range(len(sample_names)):
            ext_grain_sizes.extend(grain_sizes)

        all_cum_per = (data.iloc[0:, :]).to_numpy().tolist()

        # flatten the list of list of initial Y in a single list
        all_cum_per = [item for sublist in all_cum_per for item in sublist]

        ext_sample_names = []
        for i in range(len(sample_names)):
            for j in range(len(grain_sizes)):
                ext_sample_names.append(sample_names[i])

        cum_gsd_df = {"Grain Size [m]": ext_grain_sizes, "Sample Name": ext_sample_names, "Percentage [%]": all_cum_per}
        cum_gsd_df = pd.DataFrame(cum_gsd_df)

        fig = px.line(cum_gsd_df, x="Grain Size [m]", y="Percentage [%]",
                      title="Cumulative Grain Size Distribution Curve",
                      color="Sample Name", log_x=True)

        fig.update_layout(title_font_size=25)

        fig.update_layout(legend_bordercolor='darkgrey',
                          legend_font_size=15)

        fig.update_xaxes(type='category', autorange="reversed",
                         showline=True, mirror=True,
                         ticks='outside', linewidth=2, title_font_size=18,
                         linecolor='black', gridcolor='darkgrey')

        fig.update_yaxes(showline=True, mirror=True,
                         ticks='outside', linewidth=2,
                         linecolor='black', title_font_size=18,
                         gridcolor='darkgrey')

        fig.show()

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

    # def plot_gsd(self, samples):
    #     # filter samples given sample name
    #     df = self.df[self.df["sample name"].isin(samples)]
    #
    #     # filter only grain size, samples name and class weight
    #     df_gsd = df.set_index("sample name").iloc[:, 33:49].stack().reset_index()
    #
    #     # rename columns for future reference
    #     df_gsd.rename(columns={df_gsd.columns[1]: "gsd", df_gsd.columns[2]: "cw"}, inplace=True)
    #
    #     # create GSD figure
    #     fig = px.line(df_gsd, x="gsd", y="cw", color='sample name', title="Grain Size Distribution")
    #     fig.update_xaxes(type="log")
    #
    #     return fig
