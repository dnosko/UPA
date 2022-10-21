from src.Downloader.downloader import download
from src.Downloader.extract import extract_files
def main():
    download()
    extract_files()

if __name__ == "__main__":
    main()