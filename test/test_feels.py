import unittest
from unittest.mock import patch, MagicMock
import json
import os
import time

from tweetfeels import (TweetFeels, Tweet, TweetData)


class Test_Feels(unittest.TestCase):
    def setUp(self):
        TweetFeels._db_factory = (lambda db: MagicMock())
        TweetFeels._auth_factory = (lambda cred: MagicMock())
        TweetFeels._listener_factory = (lambda ctrl: MagicMock())
        TweetFeels._stream_factory = (lambda auth, listener: MagicMock())
        self.tweets_data_path = 'test/sample.json'

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
