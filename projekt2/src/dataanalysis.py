from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os


class DataAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.types = self.df.dtypes
        self.change_df_types()
        self.numerical = self.df.select_dtypes(include='number')
        self.categories = self.df.select_dtypes(include='category')
        self.timestamps = self.df.select_dtypes(include='timedelta')
        self.numerical_analysis = self.numerical_analysis(self.numerical)
        self.categories_values = self.get_categories_values(self.categories)
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

    def change_df_types(self):
        self.df['Date Egg'] = pd.to_datetime(self.df['Date Egg'])
        objects_df = self.df.select_dtypes(include="object")

        for i in objects_df.columns:
            self.df[i] = self.df[i].astype("category")

    def numerical_analysis(self, df):
        return df.agg({'min', 'max', 'mean', 'median'})

    def print_numerical_range(self):
        print(self.numerical_analysis.transpose().to_string())

    def print_categorical_range(self):
        print(self.categories_values.to_string())

    def print_categories_vars_unique(self):
        for i in self.categories.columns:
            print(self.categories[i].unique())

    def analyze_attributes(self):
        self.print_numerical_range()
        self.print_categorical_range()

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
        return df

    @staticmethod
    def filter_sex( df, valid=True):
        """ If valid is True, filters Sex column values to only valid sexes - Female, Male.
            If valid is False, returns incorrect values (including Nan) """
        if valid:
            return df[df['Sex'].isin(['FEMALE', 'MALE']) == True].dropna(axis=0)
        else:
            return df[df['Sex'].isin(['FEMALE', 'MALE']) == False]


    def boxplot_males_females(self, show_fig=True, fig_location=None):
        df = self.df[['Body Mass (g)', 'Species', 'Sex']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        ax = sns.boxplot(data=df, y="Body Mass (g)", x="Species", hue="Sex",
                         palette={"FEMALE": "pink", "MALE": "skyblue"},
                         hue_order=["FEMALE", "MALE"], )
        ax.legend(loc="upper center", ncol=2)
        ax.set(ylabel="Body Mass [g]", xlabel="Species", title='Body mass across species')
        self._show_fig(fig_location, show_fig)

    def histogram_species_on_island(self, show_fig=True, fig_location=None):
        df = self.df[['Island', 'Species', 'Sex']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)

        sns.displot(data=df,kind='hist', x='Species', hue='Sex', col='Island',multiple='dodge', palette={"FEMALE": "pink", "MALE": "skyblue"},
                         hue_order=["FEMALE", "MALE"])

        self._show_fig(fig_location, show_fig)

    def pair_grid(self, attr=None, palette=None, hue_order=None, show_fig=True, fig_location=None):
        df = self.df[['Species', 'Sex', 'Flipper Length (mm)', 'Culmen Length (mm)','Culmen Depth (mm)', 'Body Mass (g)']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        g = sns.PairGrid(df, hue=attr, palette=palette, hue_order=hue_order)
        g.map_offdiag(sns.scatterplot)
        g.map_diag(sns.kdeplot)
        g.add_legend()

        self._show_fig(fig_location, show_fig)

    def flipper_len_on_islands_kde(self, show_fig=True, fig_location=None):
        df = self.df[
            ['Species', 'Sex', 'Flipper Length (mm)', 'Island']]
        df = self.filter_sex(df, valid=True)
        df = self.parse_species_without_latin(df)
        ax = sns.displot(data=df, x="Flipper Length (mm)", hue='Species', col='Island', kind='kde')
        self._show_fig(fig_location, show_fig)

    def swarmplot_sex_species(self, show_fig=True, fig_location=None):
        df = self.df[['Species', 'Sex', 'Body Mass (g)',"Flipper Length (mm)", 'Culmen Length (mm)','Culmen Depth (mm)']]
        df = self.filter_sex(df, valid=True)
        df['Sex'] = df.Sex.cat.remove_unused_categories()
        df = self.parse_species_without_latin(df)
        fig, axes = plt.subplots(4, 1, figsize=(8,18))
        attr = ["Body Mass (g)", "Flipper Length (mm)", 'Culmen Length (mm)','Culmen Depth (mm)']
        i = 0
        for ax in axes:
            sns.swarmplot(data=df, x=attr[i], y='Species', hue='Sex',
                           palette={"FEMALE": "pink", "MALE": "skyblue"},
                           hue_order=["FEMALE", "MALE"], ax=ax)
            ax.set(title=f'{attr[i]} by Species')
            i += 1
        fig.tight_layout()
        self._show_fig(fig_location, show_fig)

