
import csv
import sys
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=10",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "en-US;q=0.7,en;q=0.6",
            'cookie': '__uzma=1f22a0b0-baa6-4fa9-a71d-451e2c8fcd6a; __uzmb=1602620116; __uzme=4861; VZTX=2733254163; TPL=1; CCC=18863907; CriticalCSS=6858194; .AspNetCore.Culture=c%3Dcs-CZ%7Cuic%3Dcs-CZ; _vwo_uuid_v2=D1424839DBF8E18D19F6126EFE4B45DC9|c4261905652b4bb599d831078fc529a4; __ssds=2; __ssuzjsr2=a9be0cd8e; __uzmaj2=872c22d0-babe-4a28-a326-b816a5c808b0; __uzmbj2=1602677383; i18next=cs-CZ; _gid=GA1.2.483098774.1602677384; ai_user=02ajXPMWLYcA82LQmcgmKt|2020-10-14T12:09:44.442Z; _gcl_au=1.1.613976267.1602677389; db_ui=c811ca53-36f3-5c15-45e5-355854a4ebe2; _hjTLDTest=1; _hjid=a08844ad-48f2-4648-b256-ec75750846ce; _hjIncludedInSessionSample=1; _hjAbsoluteSessionInProgress=1; db_uicd=454c9966-c325-ef24-03c8-dd90e750ee8a; PVCFLP=5; __uzmcj2=664922256883; __uzmdj2=1602677571; lb_id=b0ae2fcde80aefdf082845c369118483; SL_C_23361dd035530_KEY=178242482b9ce6820d21aac111dd0e23835adf09; __uzmc=956408239211; __uzmd=1602678241; _ga=GA1.1.1771958577.1602677384; _ga_FGLGFS7LP0=GS1.1.1602677388.1.1.1602678264.60; SL_C_23361dd035530_SID=5C40vMURNg; SL_C_23361dd035530_VID=-ibqW9xeUh6; ai_session=XhPbnATpFs7KMd15JD5gZl|1602677386866|1602678448923'
        }

def get_urls(input_file:str, output_file="data.tsv"):
    urls = open(input_file, "r")
    f_output = open(output_file, "a")
    csv_output = csv.writer(f_output, delimiter='\t')
    i = 0
    for url in urls:
        i = i +1
        if i < 83:
            continue
        url = url.replace('\n', '')
        request = Request(url, headers=headers)
        page = urlopen(request)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        name = soup.find(class_="product-name").text
        price = soup.find(class_="js-sl-price").text.split()[1]
        price = float(price.replace('.','', 1).replace(',','.',1))
        print(f"{url}\t{name}\t{price}\n")
        csv_output.writerow([url, name, price])
    urls.close()
    f_output.close()

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = "data.tsv"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    get_urls(input_file, output_file)
