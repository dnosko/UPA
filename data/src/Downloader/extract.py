import os
import fnmatch
import shutil
from glob import glob
import gzip

def extract_files(directory: str = "download_data/*/", pattern:str = '*.xml.zip') -> None:
    for subdirectory in glob(directory, recursive=True):
        for root, d, files in os.walk(subdirectory):
            for file in fnmatch.filter(files, pattern):
                filename = file.split('.', 1)[0]
                file_path = os.path.join(root, file)
                try:
                    with gzip.open(file_path, 'rb') as f_in:
                        with open(f"{root}{filename}.xml", 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                            os.remove(file_path)
                except gzip.BadGzipFile:
                    continue
