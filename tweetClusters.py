import pymongo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
#Author: 2331751v, Rishi Vinod

file = open('cluster.txt', 'a',encoding='utf-8')

def getTweetData(tweet_collection):

    #initialising empty lists to later store information.
    user_names = []
    hashtags = []
    text = []
    alldata = tweet_collection.find()

    # Extract Usernames, Hashtags and Text from database collection
    for tweet in alldata:
        username_tweets = str(tweet['username']).lower()
        hashtags_tweets = str(tweet['hashtags']).lower()
        tweet_text = str(tweet['text']).lower()
        user_names.append(username_tweets)
        hashtags.append(hashtags_tweets)
        text.append(tweet_text)

    return user_names, hashtags, text


# Visualise the data in terms of top results.
def getResults(vectorizer, group):
    k = 6
    centroids = group.cluster_centers_.argsort()[:, ::-1] # Finding the centers of the clusters and sorting them
    text = vectorizer.get_feature_names()
    for c in range(k):
        print("CLUSTER %d:" % c)
        file.write("CLUSTER %d:" % c+"\n")
        for i in centroids[c, :5]:
            print(' %s' % text[i])
            file.write(' %s' % text[i]+"\n")


# Vectorize the extracted lists and create clusters.
def clustering(usernames, hashtags, texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    k = 6

    userVec = vectorizer.fit_transform(usernames)
    hashVec = vectorizer.fit_transform(hashtags)
    textVec = vectorizer.fit_transform(texts)

    userK = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1).fit(userVec)
    hashK = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1).fit(hashVec)
    textK = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1).fit(textVec)

    return vectorizer, userK, hashK, textK



if __name__ == "__main__":

    # Setting up connection
    client = pymongo.MongoClient('localhost', 27017)
    dbName = "TwitterDump"  # set-up a MongoDatabase
    db = client[dbName]
    collName = 'TweetColl'  # here we create a collection
    collection = db[collName]
    userNames, hashTags, Texts = getTweetData(collection)
    vector, user_K, hash_K, text_K = clustering(userNames, hashTags, Texts)

    #Getting top results of usernames
    print("USERNAME CLUSTERS:")
    file.write("Top usernames per cluster:"+"\n")
    getResults(vector, user_K)

    #Getting top results of hashtags
    print("HASHTAG CLUSTERS:")
    file.write("Top hashtags per cluster:"+"\n")
    getResults(vector, hash_K)

    #Getting top results of texts
    print("TEXT CLUSTERS:")
    file.write("Top text per cluster:"+"\n")
    getResults(vector, text_K)

    file.close()