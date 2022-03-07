from face_reg.face_avt import get_avatar
from detect_object.detect import detect_vehicle
from facenet_pytorch import MTCNN
import torch
import cv2
from PIL import Image
import os
import json
import time
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
import json
from pymongo import MongoClient

f = open("../connection_string.txt", "r")
CONNECTION_STRING = str(f.read()).split("\n")[0]

#Crop face from image user
def crop_face(user_id): 
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)
    list_img = os.listdir('../user/'+ str(user_id) + '/img/')
    
    for i in list_img:
        index = 0
        img = cv2.imread('../user/'+ str(user_id) + '/img/' + i)
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img3 = Image.fromarray(img2)
        faces, pros = mtcnn.detect(img3)

        if faces is None:
            continue

        for j, (x, y, w, h) in enumerate(faces):
            if pros[j] < 0.94:
                continue
            x,y,w,h = int(x), int(y), int(w), int(h)
            temp = img[y:h, x:w]

            if temp.shape[0] < 80 and temp.shape[1] < 80:
                continue
            
            try:
                temp = cv2.resize(temp, (96,96))
            except cv2.error:
                pass
                
            try:
                cv2.imwrite('./data_process/' + str(i.split('.')[0]) + '_' + str(index) + '.jpg', temp)
                index += 1
            except cv2.error:
                pass

def get_family(user_id):
    # Extract info from text profile
    start = time.time()
    client = MongoClient(CONNECTION_STRING)
    db_name = client[user_id]
    col = db_name['profile']
    res = list(col.find())
    change = False
    item = {}

    if len(res) > 0:
        list_yes = ['Đã đính hôn', 'Đã kết hôn', 'Chung sống có đăng ký', 'Chung sống',
                        'Engaged', ' Married', 'In a civil partnership', 'In a domestic partnership']

        list_no = ['Độc thân', 'Hẹn hò', 'Tìm hiểu', 'Single', 'In a relationship', 'In an open relationship']    
        
        if res[0]['relation'] in list_yes:
            change = True
            item['family'] = 'Yes'
        elif res[0]['relation'] in list_no:
            change = True
            item['family'] = 'No'

    #From avatar 
    if not change:
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        mtcnn = MTCNN(keep_all=True, device=device)

        img = cv2.imread('../user/'+ str(user_id) + '/avt/avatar.jpg')
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img3 = Image.fromarray(img2)
        faces, pros = mtcnn.detect(img3)

        if faces is None:
            item['family'] = 'No information'
        else:
            count = 0
            for i,_ in enumerate(faces):
                if pros[i] >= 0.94:
                    count += 1

            if count > 3:
                item['family'] = 'Yes'
            else:
                item['family'] = 'No information'
    item['time'] = time.time() - start
    out = db_name['extract_family']
    if len(list(out.find())) > 0:
        out.drop()
    out.insert_one(item)
    del item['_id']    
    return item

app = Flask(__name__)
# Apply Flask CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.route('/', methods=['GET', 'POST'] )
@cross_origin(origin='*')
def home_process():
    return "Extract info"

@app.route('/family', methods=['POST'] )
@cross_origin(origin='*')
def family_process():
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
    
    temp = get_family(user_id)
    return jsonify(temp)

@app.route('/face', methods=['POST'] )
@cross_origin(origin='*')
def face_process():
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
    
    start = time.time()
    #crop face to folder data_process
    crop_face(user_id)
    #get image contain main face
    list_index = get_avatar()
    item = {}
    item['main_face'] = list_index
    item['time'] = time.time() - start

    with open('../user/'+ str(user_id) + '/main_face.json','w', encoding='utf-8') as f:
        json.dump(item, f)

    folder_img = './data_process'
    for f in os.listdir(folder_img):
        os.remove(os.path.join(folder_img, f))
    
    return jsonify(item)

@app.route('/vehicle', methods=['POST'] )
@cross_origin(origin='*')
def vehicle_process():
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
    start = time.time()
    #Get image have vehicle
    list_image_moto,list_image_car = detect_vehicle(user_id)

    #Get list image main face
    f = open('../user/'+ str(user_id) + '/main_face.json', encoding="utf-8")
    list_image_face = json.load(f)
    
    list_image_face = list_image_face['main_face']

    item = {}
    item['car'] = 'No information'
    item['moto'] = 'No infomation'
    
    if len(list_image_car) > 0:
        check_car = False
        for i in list_image_car:
            if i in list_image_face:
                check_car = True
        if check_car:
            item['car'] = 'Car with main face'
        else:
            item['car'] = 'Car without main face'

    if len(list_image_moto) > 0:
        check_moto = False
        for i in list_image_moto:
            if i in list_image_face:
                check_moto = True
        if check_moto:
            item['moto'] = 'Moto with main face'
        else:
            item['moto'] = 'Moto without main face'
    
    item['time'] = time.time() - start

    client = MongoClient(CONNECTION_STRING)
    db_name = client[user_id]
    out = db_name['extract_vehicle']
    if len(list(out.find())) > 0:
        out.drop()
    out.insert_one(item)
    del item['_id']    
    return jsonify(item)

# Start Backend
if __name__ == '__main__':
    app.run(host='', port='5000',debug=True)







