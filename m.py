import urllib
import re
import os
import json
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import csv

# set proxy
proxies = {'http': 'http://127.0.0.1:1087', 'https': 'http://127.0.0.1:1087'}
# set farfetch root link
farfetch_url = "https://www.farfetch.com"

def far_shoe_crawler(max_pages):
    # define the global variables which are called in get_item
    global csv_writer
    # create and opens a .csv file in write mode and loads in the appropriate headlings
    csv_file = open('farfect_data.csv', 'w')
    csv_writer = csv.writer(csv_file)
    # The header can be modified according to personal needs
    csv_writer.writerow(['gender','brand','sku','price','img_link','soucre'])
    # define the start page
    page = 1

    # for max_pages times
    while page <= max_pages:

        # Set the current product list link
        url = 'https://www.farfetch.com/ca/shopping/women/balenciaga/bags-purses-1/items.aspx?page=' + str(page) + '&view=90'
        # Set the current store link
        # url = 'https://www.farfetch.com/ca/shopping/women/balenciaga-crocodile-effect-tote-bag-item-15920555.aspx?storeid=10952'

        source_code = requests.get(url,proxies=proxies)
        source_code.content.decode("utf-8")
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "lxml")
        searchObj = json.loads(re.search(r'(.*) = (.*)', soup.main.script.string)[2])

        print('now page {}/{} ...'.format(page, max_pages))
        # use tqdm set progressbar
        for link in tqdm(searchObj['listingItems']['items']):
            # Pass in the current list object and format to get the content
            get_item(link)
        page += 1

    # script is executed colse .csv
    csv_file.close()
    print('All {} page(s) have been scraped!'.format(max_pages))

def get_item(item):
    # use except prevent interruption so that the loop ends
    try:
        gender = item['gender']
    except:
        gender = None
    try:
        brand = item['brand']['name']
    except:
        brand = None
    try:
        sku = brand +'-'+ item['shortDescription']
    except:
        sku = None
    try:
        price = item['priceInfo']['formattedFinalPrice']
    except:
        price = None
    try:
        img_link = get_item_item(farfetch_url + item['url'],item['brand']['name'] + '-' + item['shortDescription'])
    except:
        img_link = None
    try:
        url = farfetch_url+item['url']
    except:
        url = None
    try:
        # Write the contents to a.csv file
        csv_writer.writerow([gender,brand,sku,price,img_link,url])
    except:
        pass

# Visit the details page and download the images
def get_item_item(item_url,platform):
    source_code = requests.get(item_url, proxies=proxies)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "lxml")
    # use reg to process the node and transform JSON then get imageList
    main = json.loads(re.search(r'(.*) = (.*)', soup.main.script.string)[2])['productViewModel']['images']['main']
    url = ''
    for inx, val in enumerate(main):
        # set every image name
        img_name = platform + '_' + str(inx) + '.jpg'
        path = 'your localtion path' + platform
        # Determine if the directory exists, or create the directory
        if not os.path.isdir(path):
            os.makedirs(path)
        full_path = path + '/' + img_name
        # Concatenates the result into a string concatenated with ', '
        url += full_path
        # Download zoom type image to localtion
        urllib.request.urlretrieve(val['zoom'], full_path)
    return url


far_shoe_crawler(3)

