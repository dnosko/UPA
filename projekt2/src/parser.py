import pandas as pd
import numpy as np
import re


class DataParser:

    def __init__(self, folder, files):
        self.data_folder = folder
        self.files = files
        self.df = self.parse_data()

    def parse_data(self):
        df = pd.DataFrame()

        for file in self.files:
            with open(file, mode='r') as csv_file:
                df_tmp = pd.read_csv(csv_file)
                df = pd.concat([df, df_tmp], axis=1)
        return df
