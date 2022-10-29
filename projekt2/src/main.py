from src.downloader import DataDownloader
from src.parser import DataParser

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)
    parser.parse_data()
    print(parser.dataframes["2019"])

if __name__ == "__main__":
    main()