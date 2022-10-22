import json
import os
import fnmatch
import shutil
from glob import glob
import gzip
import zipfile


# Will not match the GVD.ZIP
def extract_files(directory: str = "download_data", pattern: str = '*.xml.zip') -> None:
    for subdirectory in glob(directory + '/*/', recursive=True):
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
                    with zipfile.ZipFile(file_path, 'r') as f_in:
                        f_in.extractall(dest_path)


def extract_files_from_caches(path_to_cache: str = "cache.json"):
    with open(path_to_cache, 'r') as f:
        dict = json.load(f)

    files = dict["downloaded"]
    for file in files:
        dest_path = file.replace('download_data', 'extract_data')
        split_file_string = dest_path.split(os.sep)

        # name
        file_name = split_file_string[-1]
        file_name_dest = file_name.split('.', 1)[0]
        split_file_string.pop()

        dest = os.sep.join(split_file_string)
        if not os.path.exists(dest):
            os.makedirs(dest)

        final_path = os.path.join(dest,file_name_dest)
        print(file)
        print(split_file_string)
        print(dest)

        try:
            with gzip.open(file, 'rb') as f_in:
                if not os.path.exists(f"{final_path}.xml"):
                    with open(f"{final_path}.xml", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
        except gzip.BadGzipFile:
            with zipfile.ZipFile(file, 'r') as f_in:
                f_in.extractall(dest)


if __name__ == "__main__":
    extract_files()
