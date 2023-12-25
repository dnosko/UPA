from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import zscore


class DataAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.original_df = df
        self.types = self.original_df.dtypes
        self.df = self.change_df_types(self.original_df)
        self.numerical = self.df.select_dtypes(include='number')
        self.categories = self.df.select_dtypes(include='category')
        self.timestamps = self.df.select_dtypes(include='timedelta')
        self.chart_dir = self.create_chart_directory('charts')

    def create_chart_directory(self, name):
        main_folder = Path(__file__).parent.parent.resolve()
        chart_dir = os.path.join(main_folder, name)
        if not os.path.isdir(chart_dir):
            try:
                print("Creating directory...")
                os.makedirs(chart_dir)
            except OSError:
                print("Creation of the directory %s failed" % os.path)

        return chart_dir

    def change_df_types(self, df):
        df_new = df
        df_new['Date Egg'] = pd.to_datetime(df['Date Egg'])
        objects_df = df.select_dtypes(include="object")

        for i in objects_df.columns:
            df_new[i] = df[i].astype("category")
        return df_new

    def numerical_analysis(self):
        print(self.original_df.describe().transpose().round(decimals=2).to_string())

    def categorical_analysis(self):
        print(self.df.describe(include=['category']).transpose().to_string())
        self.print_categories_vars_unique()

    def print_categories_vars_unique(self):
        for i in self.categories.columns:
            print(self.categories[i].unique())

    def analyze_attributes(self):
        self.numerical_analysis()
        self.categorical_analysis()

    def get_categories_values(self, categories):
        cat_vals_dic = {}
        for i in categories.columns:
            cat_vals_dic[i] = categories[i].value_counts()

        df = pd.DataFrame(cat_vals_dic.values(), index=list(cat_vals_dic.keys())).stack()
        df = pd.DataFrame(df).rename(columns={0: 'counts'})

        return df

    def _show_fig(self, fig_location: str = None, show_figure: bool = False):
        """ Saves figure to given location. If show_figure=True, shows figure. """
        if fig_location:
            location = os.path.join(self.chart_dir, fig_location)
            plt.savefig(location)

        if show_figure:
            plt.show()

    @staticmethod
    def parse_species_without_latin(df: pd.DataFrame):
        df['Species'] = df['Species'].str.split('(').str[0]
        df['Species'] = df['Species'].str.split().str[0]
        return df

    @staticmethod
    def filter_sex(df, valid=True):
        """ If valid is True, filters Sex column values to only valid sexes - Female, Male.
            If valid is False, returns incorrect values (including Nan) """
        if valid:
            return df[df['Sex'].isin(['FEMALE', 'MALE']) == True].dropna(axis=0)
        else:
            return df[(df['Sex'].isin(['FEMALE', 'MALE']) == False) & (df['Sex'].isna() == False)]

    def boxplot_males_females(self, show_fig=True, fig_location=None):
        df = self.df[['Body Mass (g)', 'Species', 'Sex']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        ax = sns.boxplot(data=df, y="Body Mass (g)", x="Species", hue="Sex",
                         palette={"FEMALE": "pink", "MALE": "skyblue"},
                         hue_order=["FEMALE", "MALE"], )
        ax.legend(loc="upper center", ncol=2)
        ax.set(ylabel="Body Mass [g]", xlabel="Species", title='Body mass across species')
        plt.tight_layout()
        self._show_fig(fig_location, show_fig)

    def histogram_species_on_island(self, show_fig=True, fig_location=None):
        df = self.df[['Island', 'Species', 'Sex']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)

        sns.displot(data=df, kind='hist', x='Species', hue='Sex', col='Island', multiple='dodge',
                    palette={"FEMALE": "pink", "MALE": "skyblue"},
                    hue_order=["FEMALE", "MALE"], legend='upper center')
        plt.tight_layout()
        self._show_fig(fig_location, show_fig)

    def pair_grid(self, attr=None, palette=None, hue_order=None, show_fig=True, fig_location=None):
        df = self.df[
            ['Species', 'Sex', 'Flipper Length (mm)', 'Culmen Length (mm)', 'Culmen Depth (mm)', 'Body Mass (g)']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        g = sns.PairGrid(df, hue=attr, palette=palette, hue_order=hue_order)
        g.map_offdiag(sns.scatterplot)
        g.map_diag(sns.kdeplot)
        g.add_legend()
        plt.tight_layout()
        self._show_fig(fig_location, show_fig)

    def flipper_len_on_islands_kde(self, show_fig, fig_location=None):
        df = self.df[
            ['Species', 'Sex', 'Flipper Length (mm)', 'Island']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        sns.displot(data=df, x="Flipper Length (mm)", hue='Species', col='Island', kind='kde', legend='upper center')
        plt.tight_layout()
        self._show_fig(fig_location, show_fig)

    def swarmplot_sex_species(self, show_fig, fig_location=None):
        df = self.df[
            ['Species', 'Sex', 'Body Mass (g)', "Flipper Length (mm)", 'Culmen Length (mm)', 'Culmen Depth (mm)']]
        df = self.filter_sex(df, valid=True)
        df['Sex'] = df.Sex.cat.remove_unused_categories()
        df = self.parse_species_without_latin(df)
        fig, axes = plt.subplots(4, 1, figsize=(8, 18))
        attr = ["Body Mass (g)", "Flipper Length (mm)", 'Culmen Length (mm)', 'Culmen Depth (mm)']
        i = 0
        for ax in axes:
            sns.swarmplot(data=df, x=attr[i], y='Species', hue='Sex',
                          palette={"FEMALE": "pink", "MALE": "skyblue"},
                          hue_order=["FEMALE", "MALE"], ax=ax)
            ax.set(title=f'{attr[i]} by Species')
            i += 1
        fig.tight_layout()
        self._show_fig(fig_location, show_fig)

    def find_missing_values(self):
        df = self.df.drop(columns=['Comments'])
        df_sex = self.filter_sex(df, valid=False)
        print(f'Sex not valid value: {len(df_sex["Sex"])}')
        df['Sex'] = df['Sex'].replace('.', np.NaN)
        df = df[df.isna().any(axis=1)]
        print(df.isna().sum())
        df = df.loc[:, (df.isna().sum(axis=0) > 1)]  # keep only columns with null values
        df = df[(df.isnull().sum(axis=1) > 1)]
        print(df.to_string())

    def find_outliers_IQR(self, df):
        df = df.select_dtypes(include='number')
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1

        outliers = df[((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
        print(outliers)
        return outliers


    def find_outliers_3sigma(self, df: pd.DataFrame, show_fig, fig_location=None):
        df_z = df.apply(zscore)
        outliers = df_z
        for num_col in outliers.columns:
            sigma3 = df[num_col].std() * 3
            outliers = outliers[(abs(outliers[num_col]) > sigma3)]
        print('**** OUTLIERS ***:\n', outliers.to_string())
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        i = 1
        cols = list(self.numerical.columns)
        axes = axes.flatten()
        for ax in axes:
            sns.histplot(data=df, x=cols[i], kde=True, stat="density", color="r",
                         ax=ax)
            sns.kdeplot(df, x=cols[i], ax=ax)

            i += 1
        fig.tight_layout()
        self._show_fig(show_figure=show_fig, fig_location=fig_location)

    def find_outliers_sex(self, sex, show_fig, fig_location=None):
        sex = sex.upper()
        df = self.df
        sex = df[df['Sex'].isin([sex]) == True].select_dtypes(include='number')
        self.find_outliers_3sigma(sex, show_fig=show_fig, fig_location=fig_location)

    def find_outliers_species(self, species, show_fig, fig_location=None):
        df = self.parse_species_without_latin(self.df)
        species = df[df['Species'].isin([species]) == True].select_dtypes(include='number')
        self.find_outliers_3sigma(species, show_fig=show_fig, fig_location=fig_location)


    def correlation(self, df):
        corr = df.corr()
        return corr

    def correlation_species(self, species):
        df = self.parse_species_without_latin(self.df)
        species_df = df[df['Species'].isin([species]) == True].select_dtypes(include='number').drop(['Sample Number'], axis=1)
        corr = self.correlation(species_df)
        print(f'Correlation {species}\n', corr.to_string())

    def correlation_chart(self, df, show_fig, fig_location=None):
        g = sns.PairGrid(df)
        g.map(sns.scatterplot)
        self._show_fig(show_figure=show_fig, fig_location=fig_location)