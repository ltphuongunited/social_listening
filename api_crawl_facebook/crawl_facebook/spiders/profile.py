import scrapy
from scrapy_splash import SplashRequest
import json
from datetime import datetime
import time
from pymongo import MongoClient

#Get connection string to connect mongoDB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]
#Get user id
f = open("id_user.txt", "r")
user_id = str(f.read()).split("\n")[0]

class FacebookLoginSpider(scrapy.Spider):
    name = 'profile'
    # Lua script to interact with js in the website while crawling
    
    
    script = """
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
                assert(splash:go{
                    splash.args.url,
                    headers=splash.args.headers
                })
            assert(splash:wait(math.random(1, 3)))
            splash:set_viewport_full()      
            assert(splash:go(args.about))
            assert(splash:wait(math.random(1, 3)))

            splash:select("div[class='_86nv _2pin']"):mouse_click()
            assert(splash:wait(math.random(1, 3)))
            splash:set_viewport_full()
            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )

            for _ = 1, """ + str(3) + """ do
                scroll_to(0, get_body_height())
                assert(splash:wait(math.random(2,3)))
            end



            return {
                cookies = splash:get_cookies(),                
                html = splash:html(),
                url = splash:url(),
                acc = args.acc
            }
        end
    """
    
    def start_requests(self):
        #Load cookie
        with open('./cookies/cookie.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)
            
        # Send splash request with facebook accounnt and lua script to crawl
        link = "https://m.facebook.com/" + user_id

            
        yield SplashRequest(
                url="https:/www.facebook.com/login",
                callback=self.parse,
                session_id="test",
                meta={
                    "splash": {
                        "endpoint": "execute", 
                        "args": {
                            "lua_source": self.script,
                            "cookies": cookies,
                            "about": link
                        }
                    }
                }
            )

    def parse(self, response):
        #Get html
        h = scrapy.Selector(response)
        pro_infos = h.css("div._55wo._2xfb._1kk1")

        item = {}
        item["name"] = h.css("div._6j_d.show ::text").extract_first()
        item["studyAt"] = ""
        item["workAt"] = ""
        item["liveAt"] = ""
        item["dob"] = ""
        item["gender"] = ""
        item["relation"] = ""
        
        #Get information profile
        for info in pro_infos:
            text = info.css("div.__gx ::text").extract_first()
            if (text in ["Học vấn", 'Education']):
                list_studyAt = info.css("div._5cds._2lcw")
                item["studyAt"] = []
                for study in list_studyAt:
                    item["studyAt"].append(study.css(" ::text").extract_first())
                if len(item["studyAt"]) == 0:
                    item["studyAt"] = item["studyAt"][0]
                else:
                    item["studyAt"] = " ; ".join(item["studyAt"])


            elif (text in ["Công việc",'Work']):
                list_workAt = info.css("div._5cds._2lcw")
                item["workAt"] = []
                for work in list_workAt:
                    item["workAt"].append(work.css(" ::text").extract_first())
                if len(item["workAt"]) == 0:
                    item["workAt"] = item["workAt"][0]
                else:
                    item["workAt"] = " ; ".join(item["workAt"])

            elif (text in ["Nơi từng sống",'Places lived']):
                list_liveAt = info.css("div._2swz._2lcw")
                item["liveAt"] = []
                for live in list_liveAt:
                    item["liveAt"].append(live.css("i.img._1-yc.profpic").xpath('@aria-label').extract_first()[:-17])
                if len(item["liveAt"]) == 0:
                    item["liveAt"] = item["liveAt"][0]
                else:
                    item["liveAt"] = " ; ".join(item["liveAt"])                                  

            elif (text in ["Thông tin cơ bản", 'Basic info']):
                list_profile = info.css("div._5cds._2lcw._5cdu")
                for each in list_profile:
                    temp = each.css("::text").extract()
                    if (temp[1] in ["Năm sinh",'Birthday'] or temp[1] in ["Ngày sinh", 'Year of birth']):
                        item["dob"] = temp[0]
                    elif (temp[1] in ["Giới tính",'Gender']):
                        item["gender"] = temp[0] 

            elif (text in ["Mối quan hệ", 'Relationship']):
                item['relation'] = info.css("div._52ja._5cds._5cdt ::text").extract_first()

        #Get time crawl
        now = datetime.now()
        now = now.utctimetuple()
        now = int(time.mktime(now))
        item["crawl_at"] = now


        #Update data to database
        client = MongoClient(CONNECTION_STRING)
        db_name = client[user_id]
        col = db_name["profile"]
        doc = col.find()
        if len(list(doc)) > 0:
            col.drop()
        
        col.insert_one(item)    
    
