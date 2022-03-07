from pyvi import ViTokenizer
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from sklearn import svm
from string import punctuation
import joblib
import pickle


sep = list(punctuation) + ['\n']
data = pd.read_csv('./model/post/data_post.csv',encoding='utf-8', sep =';')
post = []
for i in data['Text']:
    i = i.lower()
    t = ViTokenizer.tokenize(i)
    post.append(t)

post = np.array(post)

label = np.array(data['Label'])
# x_train,x_test,y_train,y_test=train_test_split(post,label,test_size=0.2)
x_train = post
y_train = label
tf_vectorizer=TfidfVectorizer(ngram_range=(1,3))
x_train_tfidf=tf_vectorizer.fit_transform(x_train)
# x_test_tfidf=tf_vectorizer.transform(x_test)
clf = svm.LinearSVC()
clf.fit(x_train_tfidf, y_train)

filename = './model/post/classify_post.sav'
joblib.dump(clf, filename)
pickle.dump(tf_vectorizer, open("./model/post/model_post.pkl", "wb"))

clf = joblib.load('./model/post/classify_post.sav')
tf_vectorizer=pickle.load(open("./model/post/model_post.pkl", 'rb'))
