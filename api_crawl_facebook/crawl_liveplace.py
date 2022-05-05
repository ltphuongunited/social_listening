from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import json
from selenium.webdriver.common.keys import Keys

options1 = Options()
options1.add_argument("--disable-notifications")
# options1.add_argument("headless")

browser = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options=options1)

browser.get("http://www.facebook.com")
sleep(2)

#Load account from acc.json to login
f = open('./acc.json', encoding="utf-8")
acc = json.load(f)
print(acc)
txtUser = browser.find_element_by_id("email")
txtUser.send_keys(acc['acc']) 

txtPass = browser.find_element_by_id("pass")
txtPass.send_keys(acc['pass'])

txtPass.send_keys(Keys.ENTER)

sleep(3)

link = "https://www.facebook.com/" + "baoduy.tranngoc" + "/about"
browser.get(link)
sleep(2)
workPlace = browser.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[4]/a/span")
workPlace.click()
sleep(5)

#rq20escxv oygrvhab
livePlaceInUser = browser.find_elements_by_class_name("c9zspvje")
livePlaces = []
for i in livePlaceInUser:
    livePlaces += [i.text]

print(livePlaces)

browser.close()