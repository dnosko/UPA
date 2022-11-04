from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)
    parser.parse_data()
    analyzer = DataAnalysis(parser.dataframes['2019'])
    analyzer.analyze_attribute()
    #print(parser.dataframes["2019"])

if __name__ == "__main__":
    main()