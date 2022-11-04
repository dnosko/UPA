import os
import numpy as np
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
from os import listdir, path
from src.constants import NUM_OF_EXPECTED_CVS

class DataDownloader:

    def __init__(self, DATASET_PATH = "parulpandey/2020-it-salary-survey-for-eu-region", folder='data/download_data/'):

        self.api = KaggleApi()
        self.api.authenticate()
        self.dataset_path = DATASET_PATH
        main_folder = Path(__file__).parent.parent.resolve()
        self.data_folder = main_folder / folder
        self.data_files = []

        if not os.path.isdir(self.data_folder):
            try:
                print("Creating directory...")
                os.makedirs(folder)
            except OSError:
                print("Creation of the directory %s failed" % os.path)

        self.update_downloaded_files()
    
    def download_data(self):
        print(self.data_folder)
        self.api.dataset_download_files(dataset=self.dataset_path, path=self.data_folder, unzip=True)
    
    def update_downloaded_files(self):
        if os.listdir(self.data_folder) == [] or len(os.listdir(self.data_folder)) < NUM_OF_EXPECTED_CVS:
            self.download_data()
        # iterate over files in data directory
        for filename in listdir(self.data_folder):
            f = path.join(self.data_folder, filename)
            # checking if it is a file
            if path.isfile(f):
                # store the name of the downloaded file
                if(filename not in self.data_files):
                    self.data_files.append(str(self.data_folder ) + "/"+  filename)


if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.download_data()