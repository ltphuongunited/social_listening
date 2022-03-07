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
    name = 'page'
    # Lua script to interact with js in the website while crawling
    
    script_login = """
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
                assert(splash:go{
                    splash.args.url,
                    headers=splash.args.headers
                })
            assert(splash:wait(math.random(1, 3)))
            splash:set_viewport_full()      

            local scroll_to = splash:jsfunc("window.scrollTo")
            local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
            )
            for _ = 1, 7 do
                scroll_to(0, get_body_height())
                assert(splash:wait(2))
            end     
            assert(splash:wait(5))  

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
        yield SplashRequest(
                url="https://m.facebook.com/timeline/app_collection/?collection_token={}%3A2409997254%3A96".format(str(user_id)),
                callback=self.parse_login,
                session_id="test",
                meta={
                    "splash": {
                        "endpoint": "execute", 
                        "args": {
                            "lua_source": self.script_login,
                            "cookies": cookies,
                        }
                    }
                }
            )

    def parse_login(self, response):
        #Get html
        h = scrapy.Selector(response)
        pages = h.css("div._1a5p")

        item = {}
        item['page_liked'] = []
        for page in pages:
            item['page_liked'].append(page.css("div._1a5r ::text").extract_first())

        #Get time crawl
        now = datetime.now()
        now = now.utctimetuple()
        now = int(time.mktime(now))
        item["crawl_at"] = now
        
        #update to database
        client = MongoClient(CONNECTION_STRING)
        db_name = client[user_id]
        col = db_name["page"]
        doc = col.find()
        
        if len(list(doc)) > 0:
            col.drop()
        
        col.insert_one(item)     
    
