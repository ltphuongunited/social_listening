from keras import backend as K
import time
from multiprocessing.dummy import Pool
K.set_image_data_format('channels_first')
import cv2
import os
import glob
import numpy as np
from numpy import genfromtxt
import tensorflow as tf
from face_reg.fr_utils import *
from face_reg.inception_network import *
from keras.models import load_model
import sys 
from collections import Counter

def triplet_loss_function(y_true, y_pred, alpha=0.3):
    anchor = y_pred[0]
    positive = y_pred[1]
    negative = y_pred[2]
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)), axis=-1)
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)), axis=-1)
    basic_loss = tf.add(tf.subtract(pos_dist, neg_dist), alpha)
    loss = tf.reduce_sum(tf.maximum(basic_loss, 0.0))
    return loss


def predict(img_1, img_2, model):
    encoding_1 = img_to_encoding(img_1, model)
    encoding_2 = img_to_encoding(img_2, model)
    dist = np.linalg.norm(encoding_1 - encoding_2)
    return dist


def get_avt(model):
    image = os.listdir('./data_process')
    image.sort(key=lambda x:int(x.split('_')[0]))
    label = []
    for index,_ in enumerate(image):
        label.append(index)
        
    image = list(map(lambda x: './data_process/' + str(x), image))    

    
    lb = -1
    for i in range(len(image) - 1):
        if label[i] > lb:
            for j in range(i + 1, len(image)):
                if (label[j] > i):
                    score = predict(image[i], image[j], model)
                    if score < 0.7:
                        label[j] = label[i]
        lb = i
    
    c = Counter(label)
    label_true = c.most_common(1)[0][0]
    res = []
    for index,i in enumerate(label):
        if i == label_true:
            temp = image[index].split('/')[-1].split('_')[0]
            res.append(temp)
    #index images have main face
    return list(set(res))
    


def get_avatar():
    global model
    model = model(input_shape = (3,96,96))
    model.compile(optimizer='adam', loss=triplet_loss_function, metrics=['accuracy'])
    load_weights_from_FaceNet(model)
    return get_avt(model)

