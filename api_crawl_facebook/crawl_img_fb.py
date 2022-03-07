
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import json
from pymongo import MongoClient
import os
import requests

#Get connection string in mongoGB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]

if __name__ == "__main__":
    options1 = Options()
    options1.add_argument("--disable-notifications")
    # options1.add_argument("headless")
    
    browser = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=options1)

    browser.get("https://www.facebook.com")
    time.sleep(2)

    #Load account from acc.json to login
    f = open('./acc.json', encoding="utf-8")
    acc = json.load(f)
    txtUser = browser.find_element_by_id("email")
    txtUser.send_keys(acc['acc']) 

    txtPass = browser.find_element_by_id("pass")
    txtPass.send_keys(acc['pass'])

    txtPass.send_keys(Keys.ENTER)

    time.sleep(3)
    
    #Go to page photos
    f = open("id_user.txt", "r")
    user_id = str(f.read()).split("\n")[0]
    link = "https://www.facebook.com/" + user_id + '/photos'

    browser.get(link)
    time.sleep(2)
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


    time.sleep(2)

    #Get image avatar
    link_avt = browser.find_element_by_css_selector("div.b3onmgus.e5nlhep0.ph5uu5jm.ecm0bbzt.spb7xbtv.bkmhp75w.emlxlaya.s45kfl79.cwj9ozl2 image").get_attribute('xlink:href')
    avt = {}
    avt['link'] = link_avt
    now = datetime.now()
    now = now.utctimetuple()
    now = int(time.mktime(now))
    avt['crawl_at'] = now

    #Download image avatar
    folder_avt = '../user/' + str(user_id) + '/avt/'
    if not os.path.exists(os.path.dirname(folder_avt)):
        os.makedirs(os.path.dirname(folder_avt))
    with open(folder_avt + 'avatar.jpg', 'wb') as file:
        file.write(requests.get(link_avt).content)

    #Upload link avatar to monggoDB
    client = MongoClient(CONNECTION_STRING)
    db_name = client[user_id]
    col1 = db_name["avt"]
    doc = col1.find()
    if len(list(doc)) > 0:
        col1.drop()
    col1.insert_one(avt)


    #Get all image
    links = []
    link_img = browser.find_elements_by_xpath("//a[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 a8c37x1j datstx6m l9j0dhe7 k4urcfbm']")
    for i in range(len(link_img)):
        links.append(link_img[i].get_attribute('href'))

    time.sleep(1)
    
    col2 = db_name["image"]
    res = list(col2.find())

    item = {}
    item['link'] = []
    
    #Create folder contain image
    folder_img = '../user/' + str(user_id) + '/img/'
    if os.path.exists(os.path.dirname(folder_img)):
        for f in os.listdir(folder_img):
            os.remove(os.path.join(folder_img, f))
    else:        
        os.makedirs(os.path.dirname(folder_img))
    
    #Download all image
    for k in range(len(links)):
        browser.get(links[k])
        time.sleep(1)
        try:
            src = browser.find_element_by_css_selector("div.bp9cbjyn.j83agx80.cbu4d94t.taijpn5t.l9j0dhe7 img").get_attribute('src')
        except:
            break

        item['link'].append(src)
        with open((folder_img + '{}.jpg').format(k), 'wb') as file:
            file.write(requests.get(src).content)

        time.sleep(1)

    if len(res) > 0:
        col2.drop()
    
    col2.insert_one(item)   
    
    time.sleep(2)
    browser.close()


