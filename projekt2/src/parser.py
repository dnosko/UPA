import pandas as pd
import numpy as np
import re

class DataParser:

    def __init__(self, folder, files=[]):
        self.data_folder = folder
        self.files = files
        self.dataframes = {}

    def parse_data(self):
        cleaned_df = pd.DataFrame()

        for file in self.files:
            with open(file, mode='r') as csv_file:
                df = pd.read_csv(csv_file)
                # cleaning up the names of the columns
                if(re.match("(\w|[0-9]|/| )*2019.csv", file)):
                    df = df.rename(columns={"Zeitstempel": "Timestamp", "Position (without seniority)": "Position"})
                    self.dataframes["2019"] = df
                elif(re.match("(\w|[0-9]|/| )*2018.csv", file)):
                    df = df.rename(columns={"Zeitstempel": "Timestamp", "Position (without seniority)": "Position", "Your level": "Seniority level"})
                    self.dataframes["2018"] = df
                else:
                    # dropping columns with almost no values or with the same values in most of the rows
                    df = df.drop(['Have you received additional monetary support from your employer due to Work From Home? If yes, how much in 2020 in EUR',
                                'Have you been forced to have a shorter working week (Kurzarbeit)? If yes, how many hours per week'], axis=1)
                    df = df.rename(columns={"Have you lost your job due to the coronavirus outbreak?": "Lost job due to Covid", "Total years of experience": "Years of experience"})
                    self.dataframes["2020"] = df
                if cleaned_df.empty:
                    cleaned_df = df.filter(['Timestamp'], axis=1)

    def concat_all_df(self) -> pd.DataFrame:
        return pd.concat([self.dataframes['2018'], self.dataframes['2019'], self.dataframes['2020']])
