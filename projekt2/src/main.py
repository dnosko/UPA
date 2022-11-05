from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)

    analyzer = DataAnalysis(parser.df)
    print(len(analyzer.types))
    analyzer.print_categories_vars_unique()

if __name__ == "__main__":
    main()