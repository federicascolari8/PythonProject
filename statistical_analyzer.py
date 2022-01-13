""" Module designated for class StatisticalAnalyzer

Author : Beatriz Negreiros
"""

from config import *


class StatisticalAnalyzer:
    """
    A class for computing statistical sedimentological parameters using sieving datasets
    """

    def __init__(self, sieving_df=None):
        """
        :param sieving_df: Pandas Dataframe containing the sieving results of a sediment sample
        """
        try:
            # Attributes
            self.original_df = sieving_df
            self.cumulative_df = pd.DataFrame()
            self.statistics_df = pd.DataFrame()
            self.__interpolation_df = pd.DataFrame()
            self.porosity_conductivity_df = pd.DataFrame()

            # Methods
            self.compute_cumulative_df()
            self.__compute_interp_df()
            self.compute_statistics_df()
            self.compute_porosity_conductivity_df()
            self.test = 2
        except Exception as e:
            logging.error("StatisticalAnalyzer property fail")
            print(e)
            pass

    def compute_cumulative_df(self):
        """
        create two new columns in the grain size dataframe, which are:
        + Percentage Fraction [%] and
        + Cummulative Percentage [%]
        :return: None
        """
        # initialize cumulative dataframe
        self.cumulative_df = self.cumulative_df.append(self.original_df)

        # create new columns float type in dataframe
        self.cumulative_df["Percentage Fraction [%]"] = np.nan
        self.cumulative_df["Cummulative Percentage [%]"] = np.nan

        # compute percentage fraction
        total_weight = self.original_df.sum()[1]
        self.cumulative_df["Percentage Fraction [%]"] = 100 * self.cumulative_df["Fraction Mass [g]"] / total_weight

        # fill cumulative percentage column
        for i, value in reversed(list(enumerate(self.cumulative_df["Percentage Fraction [%]"]))):
            if i + 1 == len(self.cumulative_df["Percentage Fraction [%]"]):
                self.cumulative_df.at[i, "Cummulative Percentage [%]"] = self.cumulative_df["Percentage Fraction [%]"][
                    i]
            else:
                cumulative = self.cumulative_df.at[i, "Percentage Fraction [%]"] \
                             + self.cumulative_df.at[i + 1, "Cummulative Percentage [%]"]
                self.cumulative_df.at[i, "Cummulative Percentage [%]"] = cumulative
        pass

    def compute_statistics_df(self):
        """
        create a dataframe with relevant statistics
        :return: None
        """
        # create columns to same statistic name and value
        self.statistics_df["Name"] = np.nan
        self.statistics_df["Value"] = np.nan

        # compute statistics
        self.__compute_ds()
        self.__mean_grain_size_dm()
        self.__geometrical_mean_dg()
        self.__sorting_index_1_ds()
        self.__fredle_index()
        self.__standard_deviation()
        self.__geometric_standard_deviation()
        self.__skewness()
        self.__kurtosis()
        self.__uniformity_coefficient()
        self.__curvature_coefficient()

        pass

    def __mean_grain_size_dm(self):

        self.statistics_df.at[9, "Name"] = "Mean Grain Size dm: [mm]"
        mean_gsdm = 0.0025 * self.__interpolation_df["Grain size (interpolated) "].sum()
        self.statistics_df.at[9, "Value"] = mean_gsdm
        pass

    def __geometrical_mean_dg(self):
        """
        compute Geometrical mean dg (simplified) by Bunte & Abt 2001 and
        fill statistics dataframe
        :return: None
        """
        self.statistics_df.at[10, "Name"] = "Geometrical mean dg"

        d16 = self.statistics_df.at[1, "Value"]
        d84 = self.statistics_df.at[7, "Value"]
        self.statistics_df.at[10, "Value"] = np.sqrt([d16 * d84])

        pass

    def __sorting_index_1_ds(self):
        """
        compute Sorting Index by Bunte & Abt 2001 and
        fill statistics dataframe
        :return: None
        """
        self.statistics_df.at[11, "Name"] = "Sorting Index 1 ds"

        d16 = self.statistics_df.at[1, "Value"]
        d84 = self.statistics_df.at[7, "Value"]
        self.statistics_df.at[11, "Value"] = np.sqrt([d84 / d16])

        pass

    def __fredle_index(self):
        """
        compute fredle_index that equals  Geometrical mean dg (simplified)
        deived by Sorting Index and fill statistic dataframe
        :return: None
        """
        self.statistics_df.at[12, "Name"] = "Fredle - Index"
        fredle_index = self.statistics_df.at[10, "Value"] / self.statistics_df.at[11, "Value"]
        self.statistics_df.at[12, "Value"] = fredle_index
        pass

    def __standard_deviation(self):
        self.statistics_df.at[13, "Name"] = "Grain Size std"
        grain_size_std = np.nanstd(self.__interpolation_df["Grain size (interpolated) "].to_numpy())
        self.statistics_df.at[13, "Value"] = grain_size_std

        pass

    def __geometric_standard_deviation(self):
        """
        computes geometric_standard_deviation by Frings 2001 et. al.
        :return:None
        """
        self.statistics_df.at[14, "Name"] = "Geometric Standard Deviation"

        # temporary dataframe geo_df to compute elements of Frings et al. (2011) equation
        geo_df = self.cumulative_df.drop("Fraction Mass [g]", axis=1)
        geo_df["Percentage Fraction [%]"] = geo_df["Percentage Fraction [%]"].shift(1, fill_value=0)
        geo_df["Teta"] = -np.log2(geo_df["Grain Sizes [mm]"])
        geo_df["Teta(i)"] = (geo_df["Teta"] + geo_df["Teta"].shift(1, fill_value=np.nan)) / 2
        geo_df["fi*Teta(i)"] = geo_df["Teta(i)"] * geo_df["Percentage Fraction [%]"] / 100
        geo_df["result"] = (geo_df["Percentage Fraction [%]"] / 100) * (
                geo_df["Teta(i)"] - geo_df["fi*Teta(i)"].sum()) ** 2

        # compute geometric_std
        geometric_std = np.sqrt(geo_df["result"].sum())
        self.statistics_df.at[14, "Value"] = geometric_std

        pass

    def __skewness(self):
        self.statistics_df.at[15, "Name"] = "Skewness"

        skewness = scipy.stats.skew(self.__interpolation_df["Grain size (interpolated) "])
        self.statistics_df.at[15, "Value"] = skewness
        pass

    def __kurtosis(self):
        self.statistics_df.at[16, "Name"] = "Kurtosis"

        kurtosis = scipy.stats.kurtosis(self.__interpolation_df["Grain size (interpolated) "])
        self.statistics_df.at[16, "Value"] = kurtosis
        pass

    def __compute_ds(self):
        # type of characteristic grain size (cgs)
        ds = [10, 16, 25, 30, 50,
              60, 75, 84, 90]

        # assign each ds value to a line of the dataframe
        for n in range(0, 9):
            # name ds
            self.statistics_df.at[n, "Name"] = "d{s}".format(s=ds[n])

            # assign value to ds
            boolean_filter = self.__interpolation_df["Cummulative (interpolated) "] == ds[n]
            ds_value = self.__interpolation_df[boolean_filter.to_list()].iat[0, 1]
            self.statistics_df.at[n, "Value"] = ds_value

        pass

    def __uniformity_coefficient(self):
        self.statistics_df.at[17, "Name"] = "Coefficient of uniformity - Cu"

        d10 = self.statistics_df.at[0, "Value"]
        d60 = self.statistics_df.at[5, "Value"]
        self.statistics_df.at[17, "Value"] = d60 / d10
        pass

    def __curvature_coefficient(self):
        self.statistics_df.at[18, "Name"] = "Curvature coefficient - Cc"

        d10 = self.statistics_df.at[0, "Value"]
        d30 = self.statistics_df.at[3, "Value"]
        d60 = self.statistics_df.at[5, "Value"]
        self.statistics_df.at[18, "Value"] = d30 ** 2 / (d60 * d10)
        pass

    def __interpolate_gs(self, ds):
        interpolated_ds = 1  # continue here
        return interpolated_ds

    def __compute_interp_df(self):
        # extract data from sample
        y = np.flip(np.array(self.cumulative_df["Grain Sizes [mm]"]))
        x = np.flip(np.array(self.cumulative_df["Cummulative Percentage [%]"]))

        # estimate grain size linearly for a increase of 0.25% of cummulative percentage
        x_vals = np.linspace(0, 100, 401)
        y_intepolated = np.interp(x_vals, x, y)

        # fill dataframe with results of interpolation
        self.__interpolation_df["Cummulative (interpolated) "] = x_vals
        self.__interpolation_df["Grain size (interpolated) "] = y_intepolated

        pass

    def compute_porosity_conductivity_df(self):
        """
        compute porosity predictors
        :return: None
        """
        # create columns to same statistic name and value
        self.porosity_conductivity_df["Name"] = np.nan
        self.porosity_conductivity_df["Porosity"] = np.nan


        # name porosity predictions by author
        self.__porosity_name()

        # compute predictors
        self.__porosity_carling()
        self.__porosity_wu()
        self.__porosity_wooster()
        self.__porosity_frings()
        self.__porosity_user()

        # compute kfs based on porosity predictors and input
        self.__compute_kfs()

        pass

    def __porosity_name(self):
        authors = ["Carling and Reader (1982)",
                   "Wu and Wang (2006)",
                   "Wooster et al. (2008)",
                   "Frings et al. (2011) ",
                   "User input"]
        for k, name in enumerate(authors):
            self.porosity_conductivity_df.at[k, "Name"] = name

        pass

    def __porosity_carling(self):
        """
        Calculates porosity estimator accoridng to Carling & Reader (1982)
        :return:
        """
        d50 = self.statistics_df.at[4, "Value"]
        carling = -0.0333 + (0.4665 / ((1000 * d50 / 1000) ** 0.21))
        self.porosity_conductivity_df.at[0, "Porosity"] = carling
        pass

    def __porosity_wu(self):
        """
        Calculates porosity estimator accoridng to Wu and Wang (2006)
        :return:
        """
        d50 = self.statistics_df.at[4, "Value"]
        wu = 0.13 + (0.21 / ((1000 * d50 / 1000 + 0.002) ** 0.21))
        self.porosity_conductivity_df.at[1, "Porosity"] = wu
        pass

    def __porosity_wooster(self):
        """
           Calculates porosity estimator accoridng to Wooster et al. (2008)
           :return:
        """
        geometric_std = self.statistics_df.at[14, "Value"]
        wooster = 0.621 * np.exp(-0.457 * geometric_std)
        self.porosity_conductivity_df.at[2, "Porosity"] = wooster
        pass

    def __porosity_frings(self):
        """
        Calculates porosity estimator accoridng to Frings et al. (2011)
        :return:
        """
        geometric_std = self.statistics_df.at[14, "Value"]
        cummulative_5mm = self.cumulative_df.at[9, "Cummulative Percentage [%]"] / 100
        frings = 0.353 - 0.068 * geometric_std + 0.146 * cummulative_5mm
        self.porosity_conductivity_df.at[3, "Porosity"] = frings
        pass

    def __porosity_user(self):

        self.porosity_conductivity_df.at[4, "Porosity"] = input["porosity"]

        pass

    def print_excel(self, file_name="statistics"):
        """
        print all attribute dataframes into excel sheet
        output is saved into local folder "plot"
        :param file_name: name of the file
        :return: None
        """

        # Creating Excel Writer Object from Pandas
        wb = openpyxl.Workbook()
        wb.save("plot/{}.xlsx".format(file_name))
        with pd.ExcelWriter("plot/{}.xlsx".format(file_name)) as writer:
            self.cumulative_df.to_excel(writer, sheet_name="Sample Summary")
            self.statistics_df.to_excel(writer, sheet_name="Statistics")
            self.porosity_conductivity_df.to_excel(writer, sheet_name="PorosityAndConductivity")
        pass

    def __compute_kfs(self):
        """
        compute kf based on user input and porosity predictions
        :return: None
        """

        self.porosity_conductivity_df["Corresponding kf [m/s]"] = np.nan

        for k, porosity in enumerate(self.porosity_conductivity_df["Porosity"]):
            kf = self.__kozeny_carman(porosity=porosity)
            self.porosity_conductivity_df.at[k, "Corresponding kf [m/s]"] = kf

        pass

    def __kozeny_carman(self, porosity=np.nan):
        """
        compute hydraulic conductivity according to Kozeny-Carman-Equation
        :param porosity: sample porosity
        :return: sample hydraulic conductivity [m\s}
        """
        kozeny_df = pd.DataFrame().append(self.cumulative_df)
        kozeny_df["D_ave_i [cm]"] = ((kozeny_df["Grain Sizes [mm]"].shift(1, fill_value=0) / 10) ** 0.404) * (
                kozeny_df["Grain Sizes [mm]"] / 10) ** 0.595
        kozeny_df["Deff_i [cm]"] = kozeny_df["Percentage Fraction [%]"] / kozeny_df["D_ave_i [cm]"]
        Deff_i_cm = 100 / kozeny_df["Deff_i [cm]"].sum()
        SF = input["SF_porosity"]
        e = porosity / (1 - porosity)
        cte = 19900

        kozeny_carman_kf = cte * ((Deff_i_cm / 100) ** 2) * (1 / (SF ** 2)) * ((e ** 3) / (1 + e))

        return kozeny_carman_kf
