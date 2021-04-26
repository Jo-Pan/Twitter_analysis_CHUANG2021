import snscrape.modules.twitter as sntwitter
import pickle
import time, os,json

from twython import Twython, TwythonError
with open("twitter_credentials.json", "r") as file:
    creds = json.load(file)
twitter = Twython(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'])

file_name = 'tweets_and_tweetids.p'
if os.path.exists(file_name):
    tweet_ids, tweets = pickle.load( open(file_name, "rb" ) )
else:
    tweets = []
    tweet_ids = []

rounds = 0
oldlen = 0
while (True):
    names, tags = pickle.load( open('names_and_tags.p', "rb" ))

    keywords = []
    for n in names:
        for t in tags:
            keywords.append(n + ' ' + t)
    
    ## ------- snsrape -------
    print("SNSCRAPE PULLING....")
    for keyword in keywords:
        old_len = len(tweet_ids)
        request = keyword + ' + since:2021-02-17 include:nativeretweets'# include:nativeretweets' 

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(request).get_items()):      
            t = {}
            t['id'] = tweet.id
            t['date'] = tweet.date
            t['content'] = tweet.content
            t['username'] = tweet.username
            t['keyword'] = keyword
            t["Liu Yu"] = False
            t["Mika"] = False
            
            for n in ['liu yu', '刘宇', 'liuyu']:
                if n in t["content"].lower():        
                    t["Liu Yu"] = True
                    break

            for n in ['mika', '米卡']:
                if n in t["content"].lower():
                    t["Mika"] = True
                    break

            if tweet.id not in tweet_ids and (t["Mika"] or t["Mika"]):
                tweet_ids.append(tweet.id)
                tweets.append(t)
        
        print(f"Keyword: {keyword}, Num Tweets +{len(tweets)-old_len} --> {len(tweets)}, Tweet Time={tweet.date}, Current time={time.ctime()}")
        pickle.dump([tweet_ids, tweets], open(file_name, "wb" ))

        
    ## ------- TWITTER API -------
    for _ in range(8):
        print("TWITTER API PULLING....")
        for keyword in keywords:
            old_len = len(tweet_ids)
            try:
                search_results = twitter.search(q=keyword, count=100)
            except TwythonError as e:
                print(e)

            for result in search_results['statuses']:
                if result['id'] in tweet_ids:
                    continue
                t = {}
                t['id'] = result['id']
                t['date'] = result['created_at']
                t['content'] = result['text']
                t['username'] = result['user']['screen_name']
                t['userid'] = result['user']['id']
                t['keyword'] = keyword
                t["Liu Yu"] = False
                t["Mika"] = False

                for n in ['liu yu', '刘宇', 'liuyu']:
                    if n in t["content"].lower():        
                        t["Liu Yu"] = True
                        break

                for n in ['mika', '米卡']:
                    if n in t["content"].lower():
                        t["Mika"] = True
                        break

                try:
                    if result['retweeted_status'] is not None:
                        t['retweet_original_username'] = result['retweeted_status']['user']['screen_name']
                        t['retweet_original_userid'] = result['retweeted_status']['user']['id']
                except:
                    pass
                
                if t["Mika"] or t["Mika"]:
                    tweet_ids.append(t['id'])
                    tweets.append(t)

            print(f"Keyword: {keyword}, Num Tweets: +{len(tweets)-old_len} --> {len(tweets)}, Current time={time.ctime()}")
        pickle.dump([tweet_ids, tweets], open(file_name, "wb" ))
        print("zzzz sleeping for 15 min ... zzz")
        time.sleep(60*15*1) # every 15min pull one time
    
#     if rounds % 2 == 0:
#         print("SLEEPING FOR 1 HOURS NOW....")
#         time.sleep(60*60*1) #sleep for two hours then starts next round
    
    

