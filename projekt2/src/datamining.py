from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import zscore


class DataMiner:
    def __init__(self, df: pd.DataFrame):
        self.original_df = df
        self.types = self.original_df.dtypes
        self.df1 = self.clear_irrelevant_columns()
        self.df2 = self.clear_irrelevant_columns()
        self.resolve_missing_values()

    def clear_irrelevant_columns(self):
        df = self.original_df[
            [
                "Species",
                "Island",
                "Body Mass (g)",
                "Flipper Length (mm)",
                "Culmen Length (mm)",
                "Culmen Depth (mm)",
            ]
        ]
        return df

    def resolve_missing_values(self):
        print("Resolving missing values...\n")
        print("ORIGINAL DATAFRAME:")
        print(self.df1)
        # METHOD ONE: in dataset one, remove rows with missing values
        self.df1 = self.df1.dropna()
        print("DATAFRAME WITHOUT ROWS WITH MISSING VALUES:")
        print(self.df1)        
        
        # METHOD TWO: replace missing vales with means for given columns
        # boolean map for rows with missing values

        df2 = self.df2.copy()
        missing_value_rows = df2[df2.isna().any(axis=1)]
        common = df2.isna().any(axis=1)
        # boolean map for rows with missing values by given species
        all_conditions = [
            (df2["Species"] == "Gentoo") & (common),
            (df2["Species"] == "Adelie") & (common),
            (df2["Species"] == "Chinstrap") & (common),
        ]

        # dataframes split by species
        gentoo_df = df2[df2["Species"] == "Gentoo"]
        adelie_df = df2[df2["Species"] == "Adelie"]
        chinstrap_df = df2[
            df2["Species"] == "Chinstrap"
        ]

        # lists containing means
        culmen_depth_means = [
            gentoo_df["Culmen Depth (mm)"].mean(),
            adelie_df["Culmen Depth (mm)"].mean(),
            chinstrap_df["Culmen Depth (mm)"].mean(),
        ]
        culmen_length_means = [
            gentoo_df["Culmen Length (mm)"].mean(),
            adelie_df["Culmen Length (mm)"].mean(),
            chinstrap_df["Culmen Length (mm)"].mean(),
        ]
        flipper_length_means = [
            gentoo_df["Flipper Length (mm)"].mean(),
            adelie_df["Flipper Length (mm)"].mean(),
            chinstrap_df["Flipper Length (mm)"].mean(),
        ]
        body_mass_means = [
            gentoo_df["Body Mass (g)"].mean(),
            adelie_df["Body Mass (g)"].mean(),
            chinstrap_df["Body Mass (g)"].mean(),
        ]

        # replace missing values with means
        df2["Culmen Depth (mm)"] = np.select(
            all_conditions, culmen_depth_means, default=df2["Culmen Depth (mm)"]
        )
        df2["Culmen Length (mm)"] = np.select(
            all_conditions, culmen_length_means, default=df2["Culmen Length (mm)"]
        )
        df2["Flipper Length (mm)"] = np.select(
            all_conditions, flipper_length_means, default=df2["Flipper Length (mm)"]
        )
        df2["Body Mass (g)"] = np.select(
            all_conditions, body_mass_means, default=df2["Body Mass (g)"]
        )
        self.df2 = df2
        print("DATAFRAME WITH REPLACED MISSING VALUES:")
        print(self.df2)

    def transformations(self):
        print("Transforming data...\n")
        print("ORIGINAL DATAFRAME:")
        self.discretise_numeric_values()
        self.transform_categorical_values()

    def create_bins(self, df, column):
        n_of_bins = 12
        min = df[column].min()
        max = df[column].max()
        df[column] = pd.cut(df[column], bins=np.linspace(min, max, n_of_bins), include_lowest=True)

    def discretise_numeric_values(self):
        df1 = self.df1.copy()
        print(df1)
        self.create_bins(df1, "Flipper Length (mm)")
        self.create_bins(df1, "Body Mass (g)")
        self.create_bins(df1, "Culmen Length (mm)")
        self.create_bins(df1, "Culmen Depth (mm)")
        self.df1 = df1
        print("DATAFRAME WITH DISCRETISED NUMERICAL VALUES:")
        print(self.df1)
        

    def transform_categorical_values(self):
        df = self.df2.copy()
        new_island_labels = {"Island": {"Torgersen": 0, "Dream": 1, "Biscoe": 2}}
        new_species_labels = {
            "Species": {
                "Gentoo": 10,
                "Chinstrap": 11,
                "Adelie": 12,
            }
        }
        df.replace(new_island_labels, inplace=True)
        df.replace(new_species_labels, inplace=True)
        self.df2 = df
        print("DATAFRAME WITH TRANSFORMED CATEGORIES:")
        print(self.df2)

