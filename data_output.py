import pymongo
import json
#Author: 2331751v, Rishi Vinod


client = pymongo.MongoClient('localhost', 27017)
dbName = "TwitterDump"  # set-up a MongoDatabase
db = client[dbName]
collName = 'TweetColl'  # here we create a collection
collection = db[collName]
tweets = collection.find()
rt_count = 0
quote_count = 0
verified_count = 0
geo_count = 0
photo_count = 0
coordinate_count = 0
generic_loc = 0
red = 0
mem = {}

for tweet in tweets:
    if tweet['media_type'] == ".jpg":
        photo_count += 1
    if tweet['retweet'] == True:
        rt_count += 1
    if tweet['quoted'] == True:
        quote_count += 1
    if tweet['verified'] == True:
        verified_count += 1
    if tweet['geoenabled'] == True:
        geo_count += 1
    if tweet['coordinates'] != None:
        coordinate_count += 1
    if tweet['place_name'] or tweet['place_country'] or tweet['country_code'] or tweet['place_coordinates']or tweet['location']!=  None:
        generic_loc += 1
    id = tweet['_id'] # Check for repeated twitter ID's/duplicate tweets
    if id not in mem:
        mem[id] = tweet
    else:
        red += 1



data = {"tweets":tweets.count(), "retweets": rt_count, "quoted": quote_count, "geoenabled": geo_count,
        "exact coordinates": coordinate_count, "generic location": generic_loc, "redundant": red ,
        'Verified': verified_count, 'Images': photo_count}

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)




