try:
    import numpy as np
    from pathlib import Path
    from matplotlib import pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    import pandas as pd
    import xlrd
    import matplotlib.ticker as mtick
    import seaborn as sns
    import re
    import locale
except:
    print(
        'Error importing necessary packages. Required packages: numpy, pathlib, matplotlib, pandas, xlrd, seaborn, re, locale')


def get_overview_df(search_in_dir, outputpath):
    """
    A function to get all information necessary to plot the data of sieving freeze cores and output it as overview sheet (.csv) file
    :param search_in_dir: string, directory to search for the datafiles
    :return: dataframe containing all infos os each sample (Pandas DataFrame), list of gravel banks (List of strings)
    """
    print('Scanning files in the folder... Please wait, this process takes time.')
    dict = {}
    # Creates dictionary of samples name vs file path
    for f in Path(search_in_dir).glob('**/*.xlsx'):
        key = f.stem
        dict.update({key: str(f)})
    kb_list = []
    grainsizes = [
        250.0,
        125.0,
        63.0,
        31.5,
        16.0,
        8.0,
        4.0,
        2.0,
        1.0,
        0.5,
        0.250,
        0.125,
        0.063,
        0.031,
        0.0039,
        0.00006]
    grainsizes = [str(f) for f in grainsizes]
    charac = ['kb', 'meas_type', 'meas_number', 'add_info', 'layer_type', 'Kampagne']
    fsa = ['<0.5mm', '<1mm', '<2mm']
    d_sed = ['d10', 'd16', 'd25', 'd50', 'dm', 'd75', 'd84', 'd90',
             'sort_coef']  # Sorting coefficient is calculated by √(d84/d16)
    total_mass = []
    columns = charac + grainsizes + fsa + total_mass + d_sed
    df = pd.DataFrame(columns=columns)

    for key in dict.keys():
        attr = re.split('_|-', key)
        print(attr)
        kb_number, meas_type, meas_number, repetition, campaign = attr[0], attr[1], attr[2], attr[3], attr[4]
        sample = meas_type + meas_number
        kb_list.append(kb_number)  # append gravel bank to the list
        data_grainsize = pd.read_excel(dict[key], sheet_name='Statistik', header=9, usecols=[1, 5], skipfooter=45)
        data_fsa = pd.read_excel(dict[key], sheet_name='Interpolation', header=8, usecols=[0, 1], nrows=3)
        error = pd.read_excel(dict[key], sheet_name='Input-data', usecols='K', header=45)
        total_mass = pd.read_excel(dict[key], sheet_name='Input-data', usecols=[10, 11])
        statistics = pd.read_excel(dict[key], sheet_name='Statistik').to_numpy()
        dm = statistics[28, 2]
        d50 = statistics[40, 2]
        d84 = statistics[43, 2]
        d90 = statistics[44, 2]
        d10 = statistics[36, 2]
        d16 = statistics[37, 2]
        d25 = statistics[38, 2]
        d75 = statistics[42, 2]
        sort_coef = (d84 / statistics[37, 2]) ** 0.5
        data_fsa.columns = ['%', 'Grain size [mm]']
        fsa_percentages = data_fsa['%'].to_numpy()
        key = key.replace("_", " ")
        key = key.replace("HM00", "KB15")
        data_grainsize.columns = ['Grain Sizes [mm]', '%']
        total_mass = total_mass.to_numpy()
        total_mass = total_mass[43, 0] + total_mass[65, 0] + total_mass[87, 0]
        df.loc[key] = pd.Series(
            {'kb': kb_number, 'meas_type': meas_type, 'meas_number': meas_number, 'add_info': repetition,
             'Kampagne': campaign, 'dm': dm, 'd10': d10, 'd16': d16, 'd25': d25, 'd50': d50, 'd75': d75,
             'sort_coef': sort_coef, 'd84': d84,
             'd90': d90, 'sieving_error': error.columns.values[0]})
        percentages = data_grainsize['%'].to_numpy()
        df.loc[key, '250.0':'6e-05'] = percentages
        df.loc[key, '<0.5mm':'<2mm'] = fsa_percentages
        df.loc[key, 'total_mass'] = total_mass
    kb_list = set(kb_list)  # take only unique values of the list
    df.to_csv(outputpath)
    return df, kb_list


#  -----------------------------------------------------------------------------------------------------------------


class FreezeCores:
    """
    A class for plotting data results from Freeze Core Sampling. All data contained in the directories designated in the __ini__ will be plotted. To avoid
    plotting certain data, simply take out the files form the folder.
    """

    def __init__(self, df, kb_list, nested_colors):
        """
        :param df: Pandas DataFrame, should have the same format as the one which is output in get_overview_df
        :param kb_list:list of strings, list of all gravelbanks from which the datafiles come
        """
        self.df = df
        self.kb_list = kb_list
        self.nested_colors = nested_colors
        self.grainsizes = [
            250.0,
            125.0,
            63.0,
            31.5,
            16.0,
            8.0,
            4.0,
            2.0,
            1.0,
            0.5,
            0.250,
            0.125,
            0.063,
            0.031,
            0.0039,
            0.00006]

    def cum_curves_kb(self, kb, linestyle_per_rep, outpath, middle_line=True, sediment_types=False):
        """
        Plot and save figures of the cumulative grain size dist. of all samples.
        :param kb: string, gravel bank in format KBXX one wants to make the plot if 'all', all gravelbanks are plotted
        :param linestyle_per_rep: dictionary of strings, linestyle to use at every repetition FCX-1 FCX-2
        :param outpath: string, path to output the figure
        :param middle_line: boolean, if True the cumulative lines are done as the average between the two repetitions FCX-1 FCX-2
        :return: saves .png figures  per gravel bank
        """
        print('Plotting graph for ', kb, '...')

        if kb is not 'all':
            df_plot = self.df[self.df.kb == kb]
        else:
            df_plot = self.df
        # campaign = df_plot.date.to_numpy()
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        plt.xscale('log')
        ax.grid(which='both', alpha=0.3)
        ax.set_ylim(bottom=0, top=100)
        grainsizes = np.array(self.grainsizes)  # transform list of grain sizes in numpy array

        for row in df_plot.index:
            percentages = df_plot.loc[row, '250.0':'6e-05']
            campaign = str(df_plot.loc[row, 'Kampagne'])
            rep = str(df_plot.loc[row, 'add_info'])
            meas_number = str(df_plot.loc[row, 'meas_number'])
            if middle_line is True:
                if rep == '1':
                    sec_row = gb + ' FC ' + meas_number + '-2 ' + campaign
                    print(sec_row)
                    try:
                        sec_percentages = df_plot.loc[sec_row, '250.0':'6e-05']
                    except:
                        print("There is only one sample of the ", row, "thus the middle line will be done with it ")
                        sec_percentages = percentages
                    middle_line_plot = (sec_percentages + percentages) / 2
                    label = gb + ' FC ' + meas_number + ' ' + campaign
                    plt.plot(grainsizes, middle_line_plot * 100, label=label,
                             color=self.nested_colors[campaign][meas_number])
            else:
                # fill_between doesnt work due to the log scale ax.fill_between(grainsizes, percentages * 100, sec_percentages * 100, color=self.nested_colors[campaign][meas_number], alpha=.1)
                plt.plot(grainsizes, percentages * 100, label=row[0:9] + '-' + row[10::],
                         color=self.nested_colors[campaign][meas_number], linewidth=0.7,
                         linestyle=linestyle_per_rep[rep])
                # plt.plot(grainsizes, percentages * 100, label=row, color=self.nested_colors[campaign][meas_number],
                #          linestyle=linestyle_per_rep[rep], linewidth=1)

        # ------------------- Rominas definition of sediment facies classes:------------------------------------
        '''grain = np.array([0.0006, 5.6, 22.6, 64, 256])
        percent_class = np.array([[0, 2.22, 38.82, 89.42, 100], [0, 2.67, 14.77, 68.27, 100], [0, 24.2, 45.2, 70.8, 100], [0, 87.2, 94.17, 97.56, 100], [0, 26.1, 76.4, 96.6, 100], [0, 3.12, 10.49, 39.99, 100]])
        labels = np.array(['Cobble/Gravel', 'Large Gravel', 'Equeal Mix', 'Fine Gravel', 'Mixed Gravel', 'Large Cobble'])
        for row in range(6):
            #print(percent_class[row, :])
            ax.plot(grain, percent_class[row, :], label=labels[row], linewidth=3, markersize=6, marker='s')'''
        # ---------------------------------------------------------------------------------------------------
        if sediment_types is True:
            #  ----Secondary axis to plot sediment classes --------------------------
            categories = ['', 'Fein-', 'Mittel-', 'Grob-', 'Fein-', 'Mittel-', 'Grob-', '']
            ticks = [0.06, 0.2, 0.63, 2, 6, 20, 63, 250]
            ax2 = ax.twiny()
            # ax2.xaxis = ax.get_xaxis()
            ax2.set_xscale('log')
            ax2.set_xlim(left=0.031, right=250)
            ax2.set_xticks(ticks, minor=False)
            ax2.set_xticklabels(categories, minor=False, horizontalalignment='right')
            ax2.tick_params(which='major', length=8)
            ax2.tick_params(which='minor', length=0)
            ax2.xaxis.tick_top()
            props = dict(boxstyle='square', fill=False, alpha=1)
            ax.text(0.22, 1.18, 'Sandkorn', fontsize=12, transform=ax.transAxes, verticalalignment='top')
            # ax.text(0.092, 1.04, '                 ', fontsize=30, transform=ax.transAxes, verticalalignment='bottom', bbox=props)
            ax.add_patch(
                plt.Rectangle((0.074, 1), 0.389, 0.21, clip_on=False, transform=ax.transAxes, linewidth=1, fill=False))
            ax.text(0.60, 1.18, 'Kieskorn', fontsize=12, transform=ax.transAxes, verticalalignment='top')
            ax.add_patch(
                plt.Rectangle((0.074 + 0.389, 1), 0.384, 0.21, clip_on=False, transform=ax.transAxes, linewidth=1,
                              fill=False))
            ax.text(0.88, 1.13, 'Steine', fontsize=12, transform=ax.transAxes, verticalalignment='top')
            ax.add_patch(
                plt.Rectangle((0.847, 1), 0.1533, 0.21, clip_on=False, transform=ax.transAxes, linewidth=1, fill=False))
            ax.text(0.003, 1.13, 'Feinstes', fontsize=7.5, transform=ax.transAxes, verticalalignment='top')
            ax.add_patch(
                plt.Rectangle((0, 1), 0.074, 0.21, clip_on=False, transform=ax.transAxes, linewidth=1,
                              fill=False))
            # ax.add_patch(plt.Rectangle((0.074, 1.105), 0.846-0.074, 1.21-1.105, clip_on=False, transform=ax.transAxes, linewidth=1, fill=False))
        #  -------------------------------------------------------------------
        a = [0.06, 0.20, 0.63, 2.00, 6.00, 20.00, 63.00, 250]
        b = np.arange(0, 110, 10)
        ax.axvline(0.1, color='black', alpha=0.3, linewidth=0.5)
        ax.axvline(1.0, color='black', alpha=0.3, linewidth=0.5)
        ax.axvline(10, color='black', alpha=0.3, linewidth=0.5)
        ax.axvline(100, color='black', alpha=0.3, linewidth=0.5)
        ax.set_yticks(b)
        ax.set_xticks(a)
        ax.tick_params(which='minor', length=0)
        ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%1.2f'))
        ax.set_xlim(left=0.031, right=250)
        ax.set_xlabel('Korngröße [mm]')
        ax.set_ylabel('Siebdurchgang [%]')
        ax.legend(loc='upper left')
        # if kb != 'all':
        plt.tight_layout()
        fig.savefig(outpath, dpi=200)
        # plt.show()

    # def fsa_kb(self, kb, outpath):
    #     """
    #     Plot an save FeinSedimentAnteile as stacked columns of the samples per gravel bank
    #     :param kb: string, gravel bank in format KBXX one wants to make the plot
    #     :param outpath: string, path to output the figure
    #     :return: saves .csv of FSA per measuring point
    #     """
    #
    #     if kb is not 'all':
    #         df_plot = self.df[self.df.kb == kb]
    #     else:
    #         df_plot = self.df
    #     # campaign = df_plot.date.to_numpy()
    #     # fig, ax = plt.subplots()
    #     df_barchart = pd.DataFrame([], columns=['<0.5mm', '<1mm', '<2mm', 'err05mm', 'err1mm', 'err2mm'])
    #     # width = 0.35
    #     for row in df_plot.index:
    #         percentages = df_plot.loc[row, '<0.5mm':'<2mm']
    #         rep = str(df_plot.loc[row, 'add_info'])
    #         # meas_number = str(df_plot.loc[row, 'meas_number'])
    #         label = row[0:8] + row[10::]
    #         all_percentages = df_plot [(df["Name"]=="Tom") & (df["Age"]==42)].loc[['<0.5mm':'<2mm']]
    #         average_per_measuring_point = all_percentages.mean(axis=0)
    #         err = abs(average_per_measuring_point - percentages)
    #         df_barchart.loc[row, '<0.5mm':'<2mm'] = average_per_measuring_point
    #         df_barchart.loc[row, 'err05mm': 'err2mm'] = err
    #     df_barchart.to_csv(outpath)

    def fsa_scatter(self, fsa, figsize, outpath):
        """
        Plot an save FeinSedimentAnteile as scatter plot of the samples for all gravel banks
        :param outpath: string, path to output the figure
        :return: saves .png figure
        """
        print('Plotting graph ..')
        fig, ax = plt.subplots(figsize=figsize)
        # kb_plot = {'KB07': 1, 'KB08': 2, 'KB15': 3, 'KB19': 4, 'KB24': 5}
        colors = {'Dez2019': 'blue', 'Mar2020': 'green', 'Nov2020': 'firebrick', 'vorher': 'blue', 'nachher': 'red'}
        sns.swarmplot(x='kb', y=fsa, data=self.df, hue='Kampagne', palette=colors, size=8, order=self.kb_list)
        # ax.scatter(self.df[['kb']], self.df[[fsa]])
        ax.grid(zorder=0)
        ax.set_ylabel('Feinsedimentanteil ' + fsa + ' [%]')
        ax.set_xlabel('Kiesbank')
        plt.tight_layout()
        fig.savefig(outpath, dpi=600)

    # TODO: method below 'goodgrains_scatter' is deprecated, has to be updated
    def goodgrains_scatter(self, infile, figsize, outpath):
        """
        Plot an save FeinSedimentAnteile as scatter plot of the samples for all gravel banks
        :param outpath: string, path to output the figure
        :return: saves .png figure
        """
        print('Plotting graph ..')
        fig, ax = plt.subplots(figsize=figsize)
        # kb_plot = {'KB07': 1, 'KB08': 2, 'KB15': 3, 'KB19': 4, 'KB24': 5}
        colors = {'Dez2019': 'tab:blue', 'Mar2020': 'tab:green', 'Nov2020': 'firebrick', 'vorspu': 'purple',
                  'nachspu': 'yellow'}
        # sns.swarmplot(x='kb', y='31,5 - 125 mm', data=infile, hue='Kampagne', palette=colors, size=8, order=self.kb_list)
        sns.boxplot(x='kb', y='31,5 - 125 mm', data=infile, hue='Kampagne', palette=colors, order=self.kb_list)
        # ax.scatter(self.df[['kb']], self.df[[fsa]])
        ax.grid(zorder=0.5)
        ax.set_ylabel('Korngrößen der FC zwischen 31,5 und 125 mm [%]', fontsize=12)
        ax.set_xlabel('Kiesbank')
        plt.tight_layout()
        fig.savefig(outpath, dpi=600)

    def error_histogram(self, german_separator=True):
        """
        Plot the frequency of the error in the measurements
        :return: saves histrogram of error
        """
        if german_separator:
            plt.rcdefaults()
            locale.setlocale(locale.LC_NUMERIC, "de_DE")
            plt.rcParams['axes.formatter.use_locale'] = True
        print('Plotting graph ..')
        error_plot = self.df[['sieving_error']] * 100
        # ax.grid('on')
        ax = error_plot.plot.hist(bins=20, alpha=0.7, grid='on', label='Siebfehler', legend=False, fontsize=11)
        plt.ylabel('\nHäufigkeit\n', fontsize=12)
        ax.set_xlabel('Messfehler [%]')
        plt.show()


if __name__ == '__main__':
    cur_dir = Path.cwd()
    linestyle_per_rep = {'1': 'solid', '2': 'dashed', '3': 'dotted', '4': 'dashed'}
    # gravelbanks = ['KB07', 'KB08', 'KB15', 'KB19', 'KB24']
    gravelbanks = ['KB08', 'KB15', 'KB19']
    nested_colors = {'Dez2019': {'1': 'blue', '2': 'royalblue', '3': 'lightskyblue', '4': 'royalblue'},
                     'Mar2020': {'1': 'darkgreen', '2': 'limegreen', '3': 'palegreen', '4': 'limegreen'},
                     'Nov2020': {'1': 'red', '2': 'darkorange', '3': 'saddlebrown', '4': 'darkorange'},
                     'vorher': {'1': 'blue', '2': 'deepskyblue', '3': 'lightskyblue', '4': 'deepskyblue'},
                     'nachher': {'1': 'red', '2': 'darkorange', '3': 'saddlebrown', '4': 'darkorange'}
                     }

    df, _ = get_overview_df(search_in_dir=str(cur_dir), outputpath='overview_fc_spuelung.csv')
    # df = pd.read_csv('overview_fc_spuelung.csv',
    #                  index_col=0)  # If the file is already available, this line reads it to directly.

    river_fc = FreezeCores(df, gravelbanks, nested_colors)
    river_fc.fsa_scatter('<2mm', (4, 2.7),
                         'C:/Users/Negreiros/VERBUND_data_analysis/09_freezecores_feinsedimentanteil/Vergleich_Sp'
                         'ülung_2mm')

    # river_fc.error_histogram()


    #  river_fc.cum_curves_kb('all', linestyle_per_rep, 'C:/Users/Negreiros/VERBUND_data_analysis/02_freezecores/figures/FC_all_Mar2020_Nov2020.png', middle_line=False, sediment_types=False)

    for gb in gravelbanks:
        river_fc.cum_curves_kb(gb, linestyle_per_rep,
                               str(cur_dir / '02_freezecores/Vergleich_Spülung/') + '/figures/' + gb + '_FC_middle.png',
                               middle_line=True, sediment_types=True)
        # river_fc.fsa_kb(gb, str(cur_dir / '09_freezecores_feinsedimentanteil') + '/Vergleich_Spülung/' + gb + '_fsa.csv')
