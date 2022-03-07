import scrapy
from scrapy_splash import SplashRequest
import json
import os

class FacebookLoginSpider(scrapy.Spider):
    name = 'check_login'

    # Lua script to interact with js in the website while crawling

    script_login = """
        function main(splash, args)
            splash:init_cookies(splash.args.cookies)
            assert(splash:go{
                splash.args.url,
                headers=splash.args.headers
            })
            assert(splash:wait(math.random(1,3)))
            splash:set_viewport_full()
            local not_login = false
            
            local element = splash:select('input[name=pass]')
            if element ~= nil then not_login = true end
            local entries = splash:history()
            local last_response = entries[#entries].response
            return {
                not_login_status = not_login,
                html = splash:html()
            }
        end
    """
    
    def start_requests(self):

        # Send splash request with facebook cookie and lua script to check if cookie is logged in or not

        with open('./cookies/cookie.json', 'r') as jsonfile:
            cookies = json.load(jsonfile)

            yield SplashRequest(
                url="https://www.facebook.com/login",
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

        # If login is fail, delete cookie

        with open('./homepage/homepage.html', 'w+', encoding="utf-8") as out:
            out.write(response.text)

        if (response.data['not_login_status']):
            os.remove('./cookies/cookie.json')
        