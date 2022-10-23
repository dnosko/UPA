from .CONSTANTS import GVD_2022_zip, TARGET_URL, DOMAIN
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool, cpu_count
import numpy as np
import json
import wget
import os

PATH_TO_SAVE = 'download_data/'


def init_worker(shared_stack):
    # declare scope of a new global variable
    global stack
    # store argument in the global variable for this process
    stack = shared_stack


def regularDownload(custom_tuple):
    name, link_name, saving_destinations = custom_tuple
    if not os.path.exists(saving_destinations + os.sep + name):
        wget.download(DOMAIN + link_name, saving_destinations + os.sep + name,)
        # send result using shared queue
        return os.path.join(saving_destinations,name)

def downloadGVZIP():
    isExist = os.path.exists(PATH_TO_SAVE)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(PATH_TO_SAVE)
    name = GVD_2022_zip.split('/')[-1]
    if not os.path.exists(PATH_TO_SAVE + os.sep + name):
        wget.download(GVD_2022_zip, PATH_TO_SAVE + os.sep + name)
        return os.path.join(PATH_TO_SAVE, name)


def downloadAllZip():
    final_stack = np.array([])

    list_of_websites = []
    for number in range(1, 11):
        number_string = str(number)
        if (len(number_string) == 1):
            number_string = '0' + number_string
        number_string = '2022-' + number_string
        link_to_website = TARGET_URL + '/' + number_string
        list_of_websites.append(link_to_website)
    list_of_websites.append(TARGET_URL + '2021-12')

    for website in list_of_websites:

        name_of_folder = website.split('/')[-1]
        print(name_of_folder)
        saving_destinations = os.path.join(PATH_TO_SAVE, name_of_folder)
        isExist = os.path.exists(saving_destinations)
        if not isExist:
            os.makedirs(saving_destinations)

        page = requests.get(website)
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("a")

        if len(links):
            if links[0].text == '[To Parent Directory]':
                links = links[1:]
            new_links = [(x.text, x['href'], saving_destinations) for x in links]

            pool = Pool(cpu_count())
            results = pool.map(regularDownload, new_links)
            results = np.asarray(results)
            results_none = results[results != None]
            final_stack = np.concatenate([final_stack, results_none])
            pool.close()
            pool.join()

    return final_stack


def download():
    stack_n = downloadAllZip()
    stack_n = stack_n.tolist()
    Path_gvd = downloadGVZIP()
    if Path_gvd is not None :
        stack_n.append(Path_gvd)

    dictionary = {
        "extracted": [],
        "downloaded": stack_n,
    }
    print("Download object count", len(stack_n))
    # Serializing json
    json_object = json.dumps(dictionary, indent=4)
    # Writing to sample.json
    with open("cache.json", "w") as outfile:
        outfile.write(json_object)
    outfile.close()

