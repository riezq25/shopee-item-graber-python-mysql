from datetime import datetime

import bs4
import mysql.connector
import requests
from mysql.connector import Error
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

options = webdriver.ChromeOptions()
options.add_argument('headless')
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"


shoppe_grabber = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="onta_store"
)

shoppe_grabber = shoppe_grabber.cursor()


def grab_item(url, delay):

    try:
        driver = webdriver.Chrome(
            options=options, desired_capabilities=capa, executable_path='C:/chromedriver.exe')
        driver.set_window_size(1440, 900)
        driver.set_page_load_timeout(10)

        driver.get(url)
        print("wait for ", delay, "s")
        time.sleep(delay)

        plain_text = driver.page_source
        soup = bs4.BeautifulSoup(plain_text, 'lxml')

        driver.close()
        driver.quit()
        # print(soup)
        item = {}

        try:
            item_id = url.replace("https://shopee.co.id/", '').split('.')
            item['id'] = item_id[len(item_id)-1]
        except:
            item['id'] = item_id[2]

        try:
            item_name = soup.find('div', {'class': 'qaNIZv'}).get_text(
            ).strip().replace("Star Seller", '')

            item['name'] = item_name
        except:
            item['name'] = None

        try:
            item_price = soup.find('div', {'class': '_3n5NQx'}).get_text(
            ).strip().replace("Rp", '').replace(".", '')

            item['price'] = item_price
        except:
            item['price'] = None

        try:
            item_des = soup.find(
                'div', {'class': '_2u0jt9'}).get_text().strip()

            item['deskripsi'] = item_des
        except:
            item['deskripsi'] = None

        try:
            item_kategori = soup.find_all('a', {'class': 'JFOy4z _20XOUy'})
            kategori = item_kategori[len(item_kategori)-1].get_text().strip()

            item['kategori'] = kategori
        except:
            item['kategori'] = None

        try:
            item_seller = soup.find(
                'div', {'class': '_3Lybjn'}).get_text().strip()

            item['seller'] = item_seller
        except:
            item['seller'] = None

        try:

            item['link'] = url
        except:
            item['link'] = None

        try:
            item_img = {}

            img = soup.find_all('div', {'class': '_3XaILN'})

            for a in range(0, len(img)):
                item_img[a] = img[a].get('style').split(';')[0].replace(
                    "background-image: url(\"", '').replace('\")', '')
            item['img'] = item_img
        except:
            item['img'] = None

        print("done get: ", url, "\n")

        return item

    except Exception:
        print('time out0')


def grab_all_item(url, start, finish, delay):
    now = start
    all_page = (finish-start)+1
    list_link = []

    for a in range(0, all_page):

        try:
            driver = webdriver.Chrome(
                options=options, desired_capabilities=capa, executable_path='C:/chromedriver.exe')
            driver.set_window_size(1440, 900)
            driver.set_page_load_timeout(10)

            driver.get(url+now)
            print("wait for ", delay, "s")
            time.sleep(delay)

            plain_text = driver.page_source