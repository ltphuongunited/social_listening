import scrapy
from scrapy_splash import SplashRequest
import json
import time 
from datetime import datetime, timedelta
from pymongo import MongoClient

#Get connection string to connect mongoDB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]
#Get user id
f = open("id_user.txt", "r")
user_id = str(f.read()).split("\n")[0]


class FacebookLoginSpider(scrapy.Spider):
    name = 'bio'
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

        link = "https://m.facebook.com/" + user_id
        # Send splash request with facebook accounnt and lua script to crawl

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
        
        now = datetime.now()
        now = now.utctimetuple()
        now = int(time.mktime(now))
        item = {}
        item["bio"] = " ".join(h.css("div._52ja._52jj._ck_._2pia ::text").extract())
        item["crawl_at"] = now

        client = MongoClient(CONNECTION_STRING)
        db_name = client[user_id]
        col = db_name["bio"]
        doc = col.find()
        
        if len(list(doc)) > 0:
            col.drop()
        
        col.insert_one(item)
