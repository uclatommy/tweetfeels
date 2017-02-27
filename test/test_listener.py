import unittest
from unittest.mock import patch, MagicMock

from tweetfeels import TweetListener
from tweetfeels import Tweet

import json
from datetime import datetime


class Test_Listener(unittest.TestCase):
    def setUp(self):
        self.tweets_data_path = 'test/sample.json'
        self.disconnect_msg = """
            {
              "disconnect":{
                "code": 4,
                "stream_name":"",
                "reason":""
              }
            }
            """

    @patch('tweetfeels.TweetFeels')
    def test_listener(self, mock_feels):
        tl = TweetListener(mock_feels)
        with open(self.tweets_data_path) as tweets_file:
            lines = filter(None, (line.rstrip() for line in tweets_file))
            for line in lines:
                tl.on_data(line)
                mock_feels.on_data.assert_called()

    @patch('tweetfeels.TweetFeels')
    def test_on_disconnect(self, mock_feels):
        tl = TweetListener(mock_feels)
        tl.reconnect_wait = MagicMock()
        tl.on_disconnect(self.disconnect_msg)
        tl.reconnect_wait.assert_called_with('linear')
        tl._controller.start.assert_called_once()

    @patch('tweetfeels.TweetFeels')
    def test_on_connect(self, mock_feels):
        tl = TweetListener(mock_feels)
        tl._waited = 60
        tl.on_connect()
        self.assertEqual(tl._waited, 0)

    @patch('tweetfeels.TweetFeels')
    def test_on_error(self, mock_feels):
        tl = TweetListener(mock_feels)
        tl.reconnect_wait = MagicMock()
        tl.on_error(420)
        tl.reconnect_wait.assert_called_with('exponential')
        self.assertEqual(tl._waited, 60)
        mock_feels.on_error.assert_called_with(420)

    @patch('tweetfeels.TweetFeels')
    def test_reconnect_wait(self, mock_feels):
        tl = TweetListener(mock_feels)
        tl._waited = 0.1
        tl.reconnect_wait('linear')
        self.assertEqual(tl._waited, 1.1)
        tl._waited = 0.1
        tl.reconnect_wait('exponential')
        tl.reconnect_wait('exponential')
        self.assertEqual(tl._waited, 0.4)


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
        dt = datetime(2017, 2, 19, 19, 14, 18)
        self.assertEqual(self.tweet['created_at'], dt)

    def test_attributes(self):
        self.assertEqual(len(self.tweet), 33)
        self.assertTrue('followers_count' in self.tweet)
        self.assertTrue(isinstance(self.tweet['created_at'], datetime))

    def test_sentiment(self):
        self.assertEqual(self.tweet.sentiment['compound'], -0.2472)
        self.assertEqual(self.tweet.sentiment['pos'], 0.087)
        self.assertEqual(self.tweet.sentiment['neu'], 0.752)
        self.assertEqual(self.tweet.sentiment['neg'], 0.161)
