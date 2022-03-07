import scrapy
from scrapy_splash import SplashRequest
import json
from datetime import datetime
import time 
from datetime import datetime, timedelta
import random as rd
from fuzzywuzzy import fuzz

from pymongo import MongoClient

#Get connection string to connect mongoDB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]
#Get user id
f = open("id_user.txt", "r")
user_id = str(f.read()).split("\n")[0]

#Similar 2 text using fuzz
def similar(text_1, text_2):
    return fuzz.token_set_ratio(text_1,text_2) > 85

class FacebookLoginSpider(scrapy.Spider):
    name = 'group'

    xpath_view_more_info = "text_exposed_hide"
    # Lua script to interact with js in the website while crawling

    
    def start_requests(self):

        script_link = """
                function main(splash, args)
                    splash:init_cookies(splash.args.cookies)
                    assert(splash:go{
                        splash.args.url,
                        headers=splash.args.headers
                    })
                    assert(splash:wait(5))
                    splash:set_viewport_full()
                    local scroll_to = splash:jsfunc("window.scrollTo")
                    local get_body_height = splash:jsfunc(
                        "function() {return document.body.scrollHeight;}"
                    )
                    for _ = 1, 2 do
                        scroll_to(0, get_body_height())
                        assert(splash:wait(1))
                    end 
                    
                    assert(splash:wait(5))

                    local divs = splash:select_all("div[class='""" + self.xpath_view_more_info + """']")
                    for _, _ in ipairs(divs) do
                        local _div = splash:select("div[class='""" + self.xpath_view_more_info + """']")
                        if _div ~= nil then
                            assert(_div:mouse_click())
                        end
                    end
                    
                    local entries = splash:history()
                    local last_response = entries[#entries].response

                    return {
                        cookies = splash:get_cookies(),
                        headers = last_response.headers,
                        html = splash:html(),
                        url = splash.url()
                    }
                end
            """


        # Send splash request with facebook cookie and lua script to crawl
        with open('./cookies/cookie.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)


        f = open("id_group.txt", "r")
        id_groups = f.read().split("\n")[:-1]

        for id_group in id_groups:        
            yield SplashRequest(
                url="https://m.facebook.com/profile.php?id={}&groupid={}".format(user_id, id_group),
                callback=self.parse,
                session_id="test",
                meta={
                    "splash": {
                        "endpoint": "execute", 
                        "args": {
                            "lua_source": script_link,
                            "cookies": cookies,
                        }
                    }
                }
            )


    def parse(self, response):
        client = MongoClient(CONNECTION_STRING)
        db_name = client[user_id]
        col = db_name["group"]

        res = list(col.find())
        
        h = scrapy.Selector(response)
        post_info = h.css("article._55wo._5rgr._5gh8.async_like")
        check = 0

        for post in post_info:
            item = {}    
            item["post_message"] = " ".join(post.css("div._il ::text").extract())
            #Check similar text in post
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
        
        if len(res) > 0:
            col.insert_many(res)