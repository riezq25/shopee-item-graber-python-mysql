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


shoppe_db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="onta_store"
)

shoppe_grabber = shoppe_db.cursor()


def checkItemDB(id_item):
    try:
        sql = "SELECT * FROM `data_item` WHERE shoppe_id=%s"
        val = (id_item,)
        shoppe_grabber.execute(sql, val)
        hasil = shoppe_grabber.fetchone()

        return hasil

    except Error as error:
        print("checkItemDB: ", error)


def checkImgDB(id_item, link):
    try:
        sql = "SELECT * FROM `gambar_item` WHERE link_gambar=%s AND shoppe_id=%s"
        val = (link, id_item)
        shoppe_grabber.execute(sql, val)
        hasil = shoppe_grabber.fetchone()

        return hasil

    except Error as error:
        print("checkImgDB: ", error)


def insertItemDB(item):
    try:
        sql = "INSERT INTO `data_item` (`shoppe_id`, `nama_item`, `harga_item`, `deskripsi_item`, `kategori_item`, `seller_item`, `lokasi_item`, `link_item`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        val = (item['id'], item['name'], item['price'], item['deskripsi'],
               item['kategori'], item['seller'], item['lokasi'], item['link'])
        shoppe_grabber.execute(sql, val)
        shoppe_db.commit()

        print(item['name'], " inserted")

    except Error as error:
        print("insertItemDB: ", error)


def insertImgDB(id_item, img):
    try:
        sql = "INSERT INTO `gambar_item` (`link_gambar`, `shoppe_id`) VALUES (%s, %s)"

        val = (img, id_item)
        shoppe_grabber.execute(sql, val)
        shoppe_db.commit()

        #print(item['name'], " inserted")

    except Error as error:
        print("insertImgDB: ", error)


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
            item['id'] = item_id[3]

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
            item_kirim = soup.find_all(
                'div', {'class': 'kIo6pj'})[3].find(
                'div').get_text().strip()

            item['lokasi'] = item_kirim
        except:
            item['lokasi'] = None

        try:

            item['link'] = url
        except:
            item['link'] = None

        try:
            item_img = {}

            img = soup.find_all('div', {'class': '_3XaILN'})

            for a in range(0, len(img)):
                item_img[a] = img[a].get('style').split(';')[0].replace(
                    "background-image: url(\"", '').replace('\")', '').replace("_tn", '')
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

            driver.get(url+str(now))
            print("get page ", (now+1), " of ", all_page, ": ", (url+str(now)))
            print("wait for ", delay, "s")
            time.sleep(delay)

            plain_text = driver.page_source
            soup = bs4.BeautifulSoup(plain_text, 'lxml')

            driver.close()
            driver.quit()
            # print(soup)
            item = []

            items = soup.find('div', {'class': 'shop-search-result-view'}).find('div', {
                'class': 'row'}).find_all('div', {'class': 'shop-search-result-view__item col-xs-2-4'})

            range_item = len(items)

            for i in range(0, range_item):
                link_item = "https://shopee.co.id"+str(items[i].find(
                    'a', href=True)['href'])

                list_link.append(link_item)

                # print("get item ", i+1, " of ",
                #     range_item, ": ", link_item)

                # item[i] = grab_item(link_item, 6)

            print("done page ", (now+1), " of ",
                  all_page, ": ", (url+str(now)))

        except Exception:
            print('time out1')

        now += 1
    return list_link


try:
    url = "https://shopee.co.id/shop/20093080/search?page="

    start_page = 0
    end_page = 29
    page_delay = 10

    links = grab_all_item(url, start_page, end_page, page_delay)

    list_items = {}

    jml_item = len(links) #semua item
    #jml_item = 6

    item_delay = 8

    for item in range(0, jml_item):
        print("get item ", (item+1), " of ", jml_item, ": ", links[item])

        list_items[item] = grab_item(links[item], item_delay)
        data_item = list_items[item]

        print("done item ", (item+1), " of ", jml_item, ": ", links[item])

        if(checkItemDB(data_item['id']) == None):
            insertItemDB(data_item)

        img = data_item['img']

        for m in range(0, len(img)):
            if(checkImgDB(data_item['id'], img[m]) == None):
                insertImgDB(data_item['id'], img[m])

    #print(list_items)

except KeyboardInterrupt:
    print("KeyboardInterrupt has been caught.")
