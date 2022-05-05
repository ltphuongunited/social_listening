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


link = "https://www.facebook.com/" + "nhatnguyenpt" + "/about"
browser.get(link)
sleep(2)
birthYear = browser.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[5]/a")
birthYear.click()
sleep(2)

birthYear = set(browser.find_elements_by_class_name("qzhwtbm6")).intersection(set(browser.find_elements_by_class_name("knvmm38d")))
# print(len(birthYear))
birthYearCrawl = []
for i in birthYear:
    if len(i.text) == 4:
        birthYearCrawl += [i.text]

print(birthYearCrawl)
# closed browser
browser.close()