import pymongo
import json
import urllib.request
import os
import random
#Author: 2331751v, Rishi Vinod

client = pymongo.MongoClient('localhost', 27017)
dbName = "TwitterDump"  # set-up a MongoDatabase
db = client[dbName]
collName = 'TweetColl'  # here we create a collection
collection = db[collName]
tweets = collection.find()
counter = 0
urlList = []

for x in tweets:
    if x['media_url']!= None:
        urlList.append(x['media_url'])
random.shuffle(urlList)
while counter < 10:
    url = urlList[counter]
    filename = "img %d" %counter+ "."+ url[-3:]
    urllib.request.urlretrieve(url, filename)
    counter += 1


# print(urlList)