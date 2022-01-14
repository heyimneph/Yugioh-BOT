import os
import requests
import numpy as np

from os import listdir
from os.path import isfile, join

from datetime import datetime
from config import LAUNCH_TIME


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
def uptime_full():
    delta_uptime = datetime.utcnow() - LAUNCH_TIME
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    time = f"{days} Day(s), {hours} Hour(s), {minutes} Minute(s), {seconds} Second(s)"
    return time


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------

def reject_outliers(data, m):
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m].tolist()


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
def list_names():
    file_path = "data/cardlists/processed"  # path tickets
    file_list = os.listdir(file_path)
    list = []
    for file in file_list:
        files = file.replace('.txt', '')
        files = files.replace('#', '')
        files = int(files)
        list.append(files)
    return max(list)


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
def yugioh_check(card):
    card = card.replace(" ", "%20")
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card}"
    page = requests.get(url).json()

    try:
        page = page['data'][0]
        return True
    except KeyError:
        return False


def yugioh_image(card):
    img_path = "data/ygo_images"

    card = card.replace(" ", "%20")
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card}"
    page = requests.get(url).json()
    page = page['data'][0]

    id = page['card_images'][0]['id']
    image = page['card_images'][0]['image_url']

    onlyfiles = [f for f in listdir(img_path) if isfile(join(img_path, f))]

    if not f"{id}.jpeg" in onlyfiles:
        img_jpg = requests.get(image)
        open(f"{img_path}/{id}.jpeg", 'wb').write(img_jpg.content)
        return f"{img_path}/{id}.jpeg"

    else:
        return f"{img_path}/{id}.jpeg"


def yugioh_prices(card):
    card = card.replace(" ", "%20")
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card}"
    page = requests.get(url).json()
    page = page['data'][0]

    data = page['card_prices'][0]

    prices = []
    for i in data:
        prices.append(data[i])
    return prices

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------



