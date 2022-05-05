from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
import json
import os
from get_id import get_id

#Get id user and write to id_user.txt - Update id to id_mapping.json
def getid_user(link):
    username =  str(link).split("?")[0].split("/")[-1]
    if username == 'profile.php':
        username = str(link).split("&")[0].split("?")[-1][3:]

    f = open('../id_mapping.json', encoding="utf-8")
    try:
        res = json.load(f)
    except json.decoder.JSONDecodeError:
        res = {}

    if username in res:
        user_id = res[username] 
    else:
        user_id = get_id([link])[0]
        res.update({username:user_id})
        with open('../id_mapping.json','w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)

    file = open("./id_user.txt", "w")
    file.write("")
    file.write(user_id)
    file.close()

#Get id groups and write to id_group.txt
def getid_group(links):
    id_groups = get_id(links)
    file = open("./id_group.txt", "w")
    for id_group in id_groups:
        file.write(id_group)
        file.write('\n')
    
    file.close()


app = Flask(__name__)
# Apply Flask CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['POST','GET'] )
@cross_origin(origin='*')
def home_process():
    return "Crawl facebook"

#Login facebook to get cookie
@app.route('/login', methods=['POST'] )
@cross_origin(origin='*')
def login_process():
    with open("./acc.json", 'w+') as jsonfile:
        json.dump(request.json, jsonfile,indent=4)
    os.system("scrapy crawl login")

    #If wrong acc then remove cookie
    os.system("scrapy crawl check_login")
    if os.path.exists('./cookies/cookie.json'):
        return {'message':'Login successfully'}
    return {'message':'Login unsuccessfully'}
 
#Crawl bio
@app.route('/bio', methods=['POST'] )
@cross_origin(origin='*')
def bio_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl bio')
    return {'message':'Bio successfully'}

#Crawl checkin
@app.route('/checkin', methods=['POST'] )
@cross_origin(origin='*')
def checkin_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl checkin')
    return {'message':'Checkin successfully'}

#Crawl page like
@app.route('/page', methods=['POST'] )
@cross_origin(origin='*')
def page_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl page')
    return {'message':'Page successfully'}

#Crawl profile
@app.route('/profile', methods=['POST'] )
@cross_origin(origin='*')
def profile_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl profile')
    return {'message':'Profile successfully'}

#Crawl timeline
@app.route('/timeline', methods=['POST'] )
@cross_origin(origin='*')
def timeline_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}
    
    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl timeline')
    return {'message':'Timeline successfully'}

#Crawl group
@app.route('/group', methods=['POST'] )
@cross_origin(origin='*')
def group_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    link_groups = request.json['link_groups']
    getid_group(link_groups)
    os.system('scrapy crawl group')
    return {'message':'Group successfully'}

#Crawl avatar and image
@app.route('/img', methods=['POST'] )
@cross_origin(origin='*')
def img_process():
    link = request.json['link']
    getid_user(link)
    os.system('python crawl_img_fb.py')
    return {'message':'Image successfully'}

# Crawl birth year
@app.route('/birth-year', methods=['POST'] )
@cross_origin(origin='*')
def bio_process():
    #If cookie exist, check it valid
    if os.path.exists('./cookies/cookie.json'):
        os.system("scrapy crawl check_login")
        if not os.path.exists('./cookies/cookie.json'):
            os.system("scrapy crawl login")        
    else:
        os.system("scrapy crawl login")

    os.system("scrapy crawl check_login")
    if not os.path.exists('./cookies/cookie.json'):
        return {'message':'Login unsuccessfully - Check account'}

    link = request.json['link']
    getid_user(link)
    os.system('scrapy crawl birthyear')
    return {'message':'Birthyear successfully'}

# Start Backend
if __name__ == '__main__':
    app.run(host='', port='5000',debug=True)
