
import scrapy
from scrapy_splash import SplashRequest
import json
from datetime import datetime, timedelta
import time 
from fuzzywuzzy import fuzz
from pymongo import MongoClient

#Get connection string to connect mongoDB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]
#Get user id
f = open("id_user.txt", "r")
user_id = str(f.read()).split("\n")[0]

#To similar 2 text using fuzz
def similar(text_1, text_2):
    return fuzz.token_set_ratio(text_1,text_2) > 85

#Convert time
def _convert_to_timestamp(the_input):

    ts = -1

    for each in  ["Hôm qua"]:
        if each in the_input:
            today = datetime.now()

            the_time = the_input.split(" ")[-1].split(":")

            d = datetime(year=today.year, month=today.month, day=today.day, hour=int(the_time[0]), minute=int(the_time[1])) - timedelta(days=1)

            ts = int(time.mktime(d.utctimetuple()))

            return ts
    
    for each in  ["tháng"]:
        if each in the_input:
            if "," in the_input:

                the_time = the_input.split(" ")

                the_hrs_mins = the_time[-1].split(":")

                d = datetime(year=int(the_time[3]), month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts

            else:

                today = datetime.now()

                the_time = the_input.split(" ")

                the_hrs_mins = the_time[-1].split(":")

                d = datetime(year=today.year, month=int(the_time[2].replace(",","")), day=int(the_time[0]), hour=int(the_hrs_mins[0]), minute=int(the_hrs_mins[1]))

                ts = int(time.mktime(d.utctimetuple()))

                return ts
    
    for each in  ["giờ"]:
        if each in the_input:

            today = datetime.now()

            the_time = the_input.split(" ")

            d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(hours=int(the_time[0]))

            ts = int(time.mktime(d.utctimetuple()))

            return ts
    
    for each in  ["phút"]:
        if each in the_input:

            today = datetime.now()

            the_time = the_input.split(" ")

            d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(minutes=int(the_time[0]))

            ts = int(time.mktime(d.utctimetuple()))

            return ts
    
    for each in  ["giây"]:
        if each in the_input:

            today = datetime.now()

            the_time = the_input.split(" ")

            d = datetime(year=today.year, month=today.month, day=today.day, hour=today.hour, minute=today.minute, second=today.second) - timedelta(seconds=int(the_time[0]))

            ts = int(time.mktime(d.utctimetuple()))
    
            return ts

class FacebookLoginSpider(scrapy.Spider):
    name = 'timeline'
    # Lua script to interact with js in the website while crawling
    
    script = """
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
                assert(splash:go{
                    splash.args.url,
                    headers=splash.args.headers
                })
            assert(splash:wait(math.random(1, 5)))
            splash:set_viewport_full()      
            assert(splash:go(args.about))
            assert(splash:wait(math.random(1,5))) 
            splash:set_viewport_full()
            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )

            for _ = 1, """ + str(4) + """ do
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
        client = MongoClient(CONNECTION_STRING)
        db_name = client[user_id]
        col = db_name["timeline"]

        res = list(col.find())
        if len(res) == 0:
            #User id has no previous data
            time_lastest_crawl = 0
        else:
            #User id has no previous data
            time_lastest_crawl = res[len(res) - 1]["time_crawl"]


        h = scrapy.Selector(response)
        post_info = h.css("article._55wo._5rgr._5gh8.async_like._1tl-")
        check = 0 
        for post in post_info:
            item = {}
            item["post_time"] = _convert_to_timestamp(post.css("div._52jc._5qc4._78cz._24u0._36xo ::text").extract_first())
            #If time post < time_lastest_crawl, this post is crawled in previous
            if item["post_time"] < time_lastest_crawl:
                break

            now = datetime.now()
            now = now.utctimetuple()
            now = int(time.mktime(now))            
            item["time_crawl"] = now
            item["post_message"] = " ".join(post.css("div.story_body_container div._5rgt._5nk5._5msi ::text").extract())

            #Check similar text to push res
            if len(res) > 0:
                for i in res:
                    if similar(i, item["post_message"]):
                        check = 1
                        break
            if check:
                check = 0
                continue
            else:
                res.append(item)
        
        if len(list(col.find())) > 0:
            col.drop()
        col.insert_many(res)



        
    
