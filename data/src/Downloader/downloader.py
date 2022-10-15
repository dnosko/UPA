from .CONSTANTS import GVD_2022_zip, TARGET_URL,DOMAIN
from bs4 import BeautifulSoup
import requests

import wget
import os

PATH_TO_SAVE = 'download_data/'



def downloadGVZIP():

    isExist = os.path.exists(PATH_TO_SAVE)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(PATH_TO_SAVE)
        name = GVD_2022_zip.split('/')[-1]
        wget.download(GVD_2022_zip,PATH_TO_SAVE+os.sep+name)
def downloadAllZip():


    list_of_websites = []
    for number in range(1,11):
        number_string = str(number)
        if (len(number_string) == 1):
            number_string = '0' + number_string
        number_string = '2022-' + number_string
        link_to_website = TARGET_URL + '/' + number_string
        list_of_websites.append(link_to_website)
    list_of_websites.append(TARGET_URL+'2021-12')

    for website in list_of_websites:

        name_of_folder = website.split('/')[-1]
        saving_destinations = PATH_TO_SAVE+os.sep+name_of_folder
        isExist = os.path.exists(saving_destinations)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(saving_destinations)

        page = requests.get(website)
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("a")
        if len(links):
            if links[0].text == '[To Parent Directory]':
                links = links[1:]
            for link in links:
                name = link.text
                link_name = link['href']
                print(DOMAIN+link_name)
                wget.download(DOMAIN+link_name, saving_destinations + os.sep +name)




def download():
    downloadAllZip()
    downloadGVZIP()
