import unittest
from unittest.mock import patch, MagicMock
import json
import os
import time
import numpy as np
from datetime import datetime, timedelta

from tweetfeels import (TweetFeels, Tweet, TweetData)


class Test_Feels(unittest.TestCase):
    def setUp(self):
        TweetFeels._db_factory = (lambda db: MagicMock())
        TweetFeels._auth_factory = (lambda cred: MagicMock())
        TweetFeels._listener_factory = (lambda ctrl: MagicMock())
        TweetFeels._stream_factory = (lambda auth, listener: MagicMock())
        self.tweets_data_path = 'test/sample.json'
        self.tweets = [
            {'created_at': 'Sun Feb 19 19:14:18 +0000 2017',
             'id_str': '833394296418082817',
             'text': 'Tweetfeels is tremendous! Believe me. I know.',
             'user': {'followers_count': '100', 'friends_count': '200',
                      'location':None}
            }, # sentiment value = 0
            {'created_at': 'Sun Feb 20 19:14:19 +0000 2017',
             'id_str': '833394296418082818',
             'text': 'Fake news. Sad!',
             'user': {'followers_count': '100', 'friends_count': '200',
                      'location':None}
            }, # sentiment value = -0.7351
            {'created_at': 'Sun Feb 21 19:14:20 +0000 2017',
             'id_str': '833394296418082819',
             'text': 'I hate it.',
             'user': {'followers_count': '100', 'friends_count': '200',
                      'location':None}
            } # sentiment value = -0.5719
            ]
        self.mock_feels = TweetFeels('abcd')
        self.feels_db = TweetData(file='./test/db.sqlite')
        self.mock_feels._feels = self.feels_db
        self.mock_tweets = [Tweet(t) for t in self.tweets]

    def tearDown(self):
        os.remove('./test/db.sqlite')

    def test_start(self):
        mock_feels = TweetFeels("abcd")
        mock_feels.tracking = []
        mock_feels.start()
        mock_feels._stream.filter.assert_not_called()
        mock_feels.tracking = ['tsla']
        mock_feels.start()
        mock_feels._stream.filter.assert_called_once()

    def test_stop(self):
        mock_feels = TweetFeels("abcd")
        mock_feels.stop()
        mock_feels._stream.disconnect.assert_called_once()

    def test_on_data(self):
        mock_feels = TweetFeels("abcd")
        mock_feels.buffer_limit = 0
        data = {'filter_level': 'low', 'text': 'test data'}
        mock_feels.on_data(data)
        mock_feels._feels.insert_tweet.assert_called_once()

        # test filtering levels
        mock_feels2 = TweetFeels("abcd")
        mock_feels2._filter_level = 'medium'
        mock_feels2.on_data(data)
        mock_feels2._feels.insert_tweet.assert_not_called()

        # test buffer limit. no inserts until we are over limit
        mock_feels2.buffer_limit = 2
        mock_feels2.filter_level = 'low'
        mock_feels2.on_data(data)
        mock_feels2._feels.insert_tweet.assert_not_called()
        mock_feels2.on_data(data)
        mock_feels2.on_data(data)
        mock_feels._feels.insert_tweet.assert_called_once()

    def test_sentiment(self):
        mock_feels = TweetFeels("abcd")
        mock_feels._feels.tweets_since = MagicMock(return_value=[])
        mock_feels._sentiment = 0.5
        mock_feels._latest_calc = datetime(2017, 1, 1, 0, 0, 0)
        mock_feels._feels.start = datetime(2017, 1, 1, 0, 0, 0)
        mock_feels._feels.end = datetime(2017, 1, 1, 0, 0, 0)
        self.assertEqual(mock_feels.sentiment, 0.5)

    def test_buffer(self):
        mock_feels = TweetFeels('abcd')
        mock_feels.buffer_limit = 5
        feels_db = TweetData(file='sample.sqlite')
        mock_feels._feels = feels_db
        with open(self.tweets_data_path) as tweets_file:
            lines = list(filter(None, (line.rstrip() for line in tweets_file)))
            for line in lines[0:3]:
                t = Tweet(json.loads(line))
                mock_feels.on_data(t)
            self.assertEqual(len(mock_feels._tweet_buffer), 3)
            for line in lines[3:6]:
                t = Tweet(json.loads(line))
                mock_feels.on_data(t)
            time.sleep(1) #this waits for items to finish popping off the buffer
            self.assertEqual(len(mock_feels._tweet_buffer), 0)
            dfs = [df for df in mock_feels._feels.all]
            self.assertEqual(len(dfs[0]), 6)
        os.remove('sample.sqlite')

    def test_sentiment_comprehensive(self):
        sentiment = 0.0
        for t in self.mock_tweets:
            self.feels_db.insert_tweet(t)
            if t['sentiment']!=0:
                # print(f'0.99*{sentiment} + 0.01*{t["sentiment"]}')
                sentiment = 0.99*sentiment + 0.01*t['sentiment']
                # print(f'sentiment = {sentiment}')
        self.mock_feels.clear_buffer()
        # calc = 0*0.99**2 + 0.01*0.99*-0.7531 + 0.01*-0.5719
        #      = -0.01299649
        self.mock_feels._latest_calc = self.mock_feels._feels.start
        self.assertTrue(np.isclose(self.mock_feels.sentiment, sentiment))
        self.assertEqual(self.mock_feels._latest_calc,
                         self.mock_feels._feels.end)

    def test_sentiments(self):
        for t in self.mock_tweets:
            self.feels_db.insert_tweet(t)
        self.mock_feels.clear_buffer()
        self.mock_feels.calc_every_n = 1
        start = datetime(2017, 2, 19, 0, 0, 0)
        dt = timedelta(days=1)
        sentiment = self.mock_feels.sentiments(strt=start, delta_time=dt)
        self.assertTrue(np.isclose(next(sentiment), 0))
        self.assertTrue(np.isclose(next(sentiment), -0.007351))
        self.assertTrue(np.isclose(next(sentiment), -0.01299649))
        for s in sentiment:
            print(s)
        self.assertEqual(self.mock_feels._latest_calc,
                         self.mock_feels._feels.end)
