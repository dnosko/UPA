import os
import fnmatch
import shutil
from glob import glob
import gzip

def extract_files(directory: str = "download_data", pattern:str = '*.xml.zip') -> None:
    for subdirectory in glob(directory+'/*/', recursive=True):
        for root, d, files in os.walk(subdirectory):
            for file in fnmatch.filter(files, pattern):
                filename = file.split('.', 1)[0]
                file_path = os.path.join(root, file)
                dest_path = root.replace(directory, 'extract_data')
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                try:
                    with gzip.open(file_path, 'rb') as f_in:
                        if not os.path.exists(f"{dest_path}{filename}.xml"):
                            with open(f"{dest_path}{filename}.xml", 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                except gzip.BadGzipFile:
                    continue
