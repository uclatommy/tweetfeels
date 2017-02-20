import unittest
from tweetfeels import TweetListener
from tweetfeels import Tweet
import json


class Test_Listener(unittest.TestCase):
    def setUp(self):
        self.tweets_data_path = 'test/sample.json'

    def test_listener(self):
        tl = TweetListener(None, None)
        with open(self.tweets_data_path) as tweets_file:
            lines = filter(None, (line.rstrip() for line in tweets_file))
            for line in lines:
                self.assertTrue(tl.on_data(line))

class Test_Tweet(unittest.TestCase):
    def setUp(self):
        self.tweet_file = 'test/tweet.json'
        self.tweet = None
        with open(self.tweet_file) as twt_file:
            lines = list(filter(None, (line.rstrip() for line in twt_file)))
            self.tweet = Tweet(json.loads(lines[0]))

    def test_tweet_keys(self):
        self.assertEqual(self.tweet['followers_count'], 83)
        self.assertEqual(self.tweet['friends_count'], 303)
        self.assertTrue(len(self.tweet)>0)
        self.assertEqual(self.tweet['created_at'], '2017-02-19 19:14:18')

    def test_attributes(self):
        self.assertEqual(len(self.tweet), 29)
        self.assertTrue('followers_count' in self.tweet)
