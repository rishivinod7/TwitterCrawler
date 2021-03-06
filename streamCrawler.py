import tweepy
import json
from pymongo import MongoClient
from datetime import datetime
import time
import sys

import emoji
import re

#Author: 2331751v, Rishi Vinod
#  please put your credentials below - very important
consumer_key = ""
consumer_secret =""
access_token =""
access_token_secret =""


auth = tweepy.OAuthHandler(consumer_key, consumer_secret )
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
if (not api):
    print('Can\'t authenticate')
    print('failed cosumeer id ----------: ', consumer_key )
# set DB DETAILS


# this is to setup local Mongodb
client = MongoClient('localhost',27017) #is assigned local port
dbName = "TwitterDump" # set-up a MongoDatabase
db = client[dbName]
collName = 'TweetColl' # here we create a collection
dataColl = 'DataColl'
collection = db[collName] #  This is for the Collection  put in the DB
coll2 = db[dataColl]
rt_count = 0

# tweetcount = db.collection.count()
# print ("number of tweets collected:", tweetcount)

def strip_emoji(text):
    #  copied from web - don't remember the actual link
    new_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    return new_text

def cleanList(text):
    #  copied from web - don't remember the actual link
    #remove emoji it works
    text = strip_emoji(text)
    # Remove URLs
    text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', str(text), flags=re.MULTILINE)
    # Remove new lines
    text = re.sub(r'/\r?\n|\r/', '', str(text), flags=re.MULTILINE)
    # Remove broken symbols
    text = re.sub(r'&amp;', '', str(text), flags=re.MULTILINE)

    text.encode("ascii", errors="ignore").decode()

    return text

def processTweets(tweet):
    #  this module is for cleaning text and also extracting relevant twitter feilds
    # initialise placeholders
    place_countrycode  =None
    place_name  =None
    place_country =None
    place_coordinates =None
    source =None
    exactcoord =None
    place=None
    rt = False
    is_image = False
    is_vid = False
    media_type =None
    media_url = None
    quoted = False

    # print(t)

    # Pull important data from the tweet to store in the database.
    try:
        created = tweet['created_at']
        quoted = tweet['is_quote_status']
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        verified = tweet['user']['verified']
        text = tweet['text']  # The entire body of the Tweet
        entities = tweet['entities']
        source = tweet['source']
        geoenabled = tweet['user']['geo_enabled']
        location = tweet['user']['location']
        exactcoord = tweet['coordinates']

    except Exception as e:
        # if this happens, there is something wrong with JSON, so ignore this tweet
        print("exc",e)
        return None

    try:
        # // deal with truncated
        if(tweet['truncated'] == True):
            text = tweet['extended_tweet']['full_text']
        elif(text.startswith('RT') == True):
            # print(' tweet starts with RT **********')
            rt = True
            # print(text)
            try:
                if( tweet['retweeted_status']['truncated'] == True):
                    # print("in .... tweet.retweeted_status.truncated == True ")
                    text = tweet['retweeted_status']['extended_tweet']['full_text']
                    # print(text)
                else:
                    text = tweet['retweeted_status']['full_text']

            except Exception as e:
                pass

    except Exception as e:
        print(e)
    text = cleanList(text)

    if "media" in entities:
        media_url = entities["media"][0]["media_url"]
        media_type = media_url[-4:]
    mentions =entities['user_mentions']
    mList = []

    for x in mentions:
        mList.append(x['screen_name'])
    hashtags = entities['hashtags']  # Any hashtags used in the Tweet
    hList =[]
    for x in hashtags:
        hList.append(x['text'])
    # if hashtags == []:
    #     hashtags =''
    # else:
    #     hashtags = str(hashtags).strip('[]')


    coordinates = None
    if(exactcoord):
        coordinates = exactcoord['coordinates']




    if ((geoenabled) and (text.startswith('RT') == False)):
        try:
            if(tweet['place']):
                # print(tweet['place'])
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_countrycode   = tweet['place']['country_code']
                place_coordinates   = tweet['place']['bounding_box']['coordinates']
        except Exception as e:
            print(e)
            print('error from place details - maybe AttributeError: ... NoneType ... object has no attribute ..full_name ...')

    tweet1 = {'_id' : tweet_id, 'date': created, 'username': username,  'text' : text,  'geoenabled' : geoenabled,  'coordinates' : coordinates,  'location' : location,  'place_name' : place_name, 'place_country' : place_country, 'country_code': place_countrycode,  'place_coordinates' : place_coordinates, 'hashtags' : hList
        , 'mentions' : mList, 'source' : source, 'retweet' : rt, 'quoted' : quoted,
              'verified':verified,'media_type' : media_type, 'media_url':media_url}

    return tweet1

def search_trends(api): ## Shows the 10 most recent trends on twitter in the UK
    trends = api.trends_place(23424975)[0]["trends"]      # WOE ID for UK is 23424975

    trend_keywords = []
    for trend in trends:
        trend_keywords.append(trend["name"])

    print("Trending keywords:", trend_keywords, "\n")

    return trend_keywords

class StreamListener(tweepy.StreamListener):
  #This is a class provided by tweepy to access the Twitter Streaming API.

    global geoEnabled
    global geoDisabled


    time_limit = 300

    def on_connect(self):

      self.start_time = time.time()
    # Called initially to connect to the Streaming API
      print("You are now connected to the streaming API.")



    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        if (time.time() - self.start_time) < self.time_limit:
            #This is where each tweet is collected
            # let us load the  json data
            t = json.loads(data)
            #  now let us process the tweet so that we will deal with cleaned and extracted JSON
            tweet = processTweets(t)
            print(tweet)

            # now insert it
            #  for this to work you need to start a local mongodb server
            try:
                collection.insert_one(tweet)
            except Exception as e:
                print("error",e)
                # this means some Mongo db insertion error
        else:
            print("Time limit reached.")




#Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.

Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019] # UK and Ireland
# Words_UK =["Boris", "Prime Minister", "Tories", "UK", "London", "England", "Manchester", "Sheffield", "York", "Southampton", \
#  "Wales", "Cardiff", "Swansea" ,"Banff", "Bristol", "Oxford", "Birmingham" ,"Scotland", "Glasgow", "Edinburgh", "Dundee", "Aberdeen", "Highlands" \
# "Inverness", "Perth", "St Andrews", "Dumfries", "Ayr" \
# "Ireland", "Dublin", "Cork", "Limerick", "Galway", "Belfast"," Derry", "Armagh" \
# "BoJo", "Labour", "Liberal Democrats", "SNP", "Conservatives", "First Minister", "Surgeon", "Chancelor" \
# "Boris Johnson", "BoJo", "Keith Stramer"]
Words_UK = search_trends(api)

print("Tracking: " + str(Words_UK))
#  here we ste the listener object
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)
streamer.filter(locations= Loc_UK, track = Words_UK, languages = ['en'], is_async=True) #locations= Loc_UK, track = Words_UK,
#  the following line is for pure 1% sample
# we can only use filter or sample - not both together
# streamer.sample(languages = ['en'])

Place =  'London'
Lat   =  '51.450798'
Long  =  '-0.137842'
geoTerm=Lat+','+Long+','+'10km'
#

last_id =  None
counter =0
sinceID = None

results = True

while results:
    # print(geoTerm)

    if (counter < 180 ):
        try:
            results = api.search(geocode=geoTerm, count=100, lang="en", tweet_mode='extended', max_id=last_id)
            # media_files = set()
            # for status in results:
            #     media = status.entities.get('media', [])
            # if (len(media) > 0):
            #     media_files.add(media[0]['media_url'])
            print("results: ",results)
        except Exception as e:
            print(e)
        counter += 1
    else:
        #  the following let the crawler to sleep for 15 minutes; to meet the Twitter 15 minute restriction
        time.sleep(15*60)

#
