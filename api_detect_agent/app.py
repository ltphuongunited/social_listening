import joblib
import pickle
from pyvi import ViTokenizer
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
import json
import time
from pymongo import MongoClient

#Get connection string to connect mongoDB
f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]

#Model classification text
def classify(article_text,post=True):
    #post = True --> post, post = False --> page
    if post:
        clf = joblib.load('./model/post/classify_post.sav')
        tf_vectorizer=pickle.load(open("./model/post/model_post.pkl", 'rb'))
    else:
        clf = joblib.load('./model/page/classify_page.sav')
        tf_vectorizer=pickle.load(open("./model/page/model_page.pkl", 'rb'))

    article = tf_vectorizer.transform([ViTokenizer.tokenize(article_text)])
    return clf.predict(article)[0]

def detect(user_id):
    start = time.time()
    client = MongoClient(CONNECTION_STRING)
    db_name = client[user_id]

    item = {}
    item['feature'] = ''
    item['isAGENT'] = 'No'


    col = db_name["timeline"]
    res = list(col.find())
    count = 0    
    for i in res:
        if classify(i['post_message']):
            count += 1

    if count > 5:
        item['feature'] = 'timeline'
        item['isAGENT'] = 'Yes'
            
    else:
        col = db_name["group"]
        res = list(col.find())
        count = 0
        for i in res:
            if classify(i['post_message']):
                count += 1

        if count > 5:
            item['feature'] = 'group'
            item['isAGENT'] = 'Yes'

        else:
            col = db_name["profile"]
            res = list(col.find())

            if len(res) > 0 and classify(res[0]['workAt'],False):
                item['feature'] = 'profile'
                item['isAGENT'] = 'Yes'     

            else:
                col = db_name["page"]
                res = list(col.find())
                count = 0
                if len(res) > 0:
                    for i in res[0]['page_liked']:
                        if classify(i,False):
                            count += 1

                if count > 7:
                    item['feature'] = 'page like'
                    item['isAGENT'] = 'Yes'
 
                else:
                    col = db_name["bio"]
                    res = list(col.find())
                    if len(res) > 0:
                        if classify(res[0]['bio']):
                            item['feature'] = 'bio'
                            item['isAGENT'] = 'Yes'


    item['time_detect'] = time.time() - start
    out = db_name['agent']
    if len(list(out.find())) > 0:
        out.drop()
    out.insert_one(item)

    del item['_id']    
    return item

app = Flask(__name__)
# Apply Flask CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/agent', methods=['POST'] )
@cross_origin(origin='*')
def agent_process():
    link = request.json['link']
    username =  str(link).split("?")[0].split("/")[-1]
    if username == 'profile.php':
        username = str(link).split("&")[0].split("?")[-1][3:]
    
    f = open('../id_mapping.json', encoding="utf-8")
    try:
        res = json.load(f)
    except json.decoder.JSONDecodeError:
        res = {}
    
    #If user_id exist in mapping then this user has crawl data
    if username in res:
        user_id = res[username]
    else:
        return {'message':"No data crawl for this user"}
    
    temp = detect(user_id)
    return jsonify(temp)
    
# Start Backend
if __name__ == '__main__':
    app.run(host='', port='5000',debug=True)






