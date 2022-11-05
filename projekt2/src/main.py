from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)
    parser.parse_data()
    df = parser.concat_all_df()
    analyzer = DataAnalysis(df)

if __name__ == "__main__":
    main()