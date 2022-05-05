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

link = "https://www.facebook.com/" + "dinosg" + "/about"
browser.get(link)
sleep(2)
workPlace = browser.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[3]/a")
workPlace.click()
sleep(5)

#rq20escxv oygrvhab
workType = browser.find_elements_by_class_name("ii04i59q")
workTypeCrawl = []
for i in workType:
    workTypeCrawl += [i.text]

# print(workTypeCrawl)
# công nhân, hành chính, kỹ thuật, TX con người, TX tự nhiên, văn hóa nghệ thuật.
for workable in workTypeCrawl:
    detectWork = workable.lower()
    conditionEngineer = [detectWork.find("software"),
        detectWork.find("engineer"),
        detectWork.find("computer"),
        detectWork.find("kỹ thuật"),
        detectWork.find("công nghệ"),
        detectWork.find("phần mềm"),
        detectWork.find("it")]
    
    conditionOnPeople = [detectWork.find("marketing"),
        detectWork.find("teacher"),
        detectWork.find("human"),
        detectWork.find("tiếp thị"),
        detectWork.find("giáo viên"),
        detectWork.find("con người"),
        detectWork.find("sư phạm"),
        detectWork.find("education")]

    conditionOnAdmin = [detectWork.find("kế toán"),
        detectWork.find("văn phòng"),
        detectWork.find("bank"),
        detectWork.find("ngân hàng"),
        detectWork.find("quân đội"),
        detectWork.find("công an"),
        detectWork.find("police"),
        detectWork.find("military")]

    if any(x != -1 for x in conditionEngineer):
        print("Kỹ thuật")
        break
    elif any(x != -1 for x in conditionOnPeople):
        print("TX con người")
    elif any(x != -1 for x in conditionOnAdmin):
        print("Hành chính")
    else:
        print("Công nhân")
# closed browser
browser.close()