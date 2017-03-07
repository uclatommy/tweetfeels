import unittest
from tweetfeels import TweetData
from tweetfeels import Tweet
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import numpy as np


class Test_Data(unittest.TestCase):
    def setUp(self):
        self.tweets_data_path = 'test/sample.json'
        self.db = './test.sqlite'
        self.feels_db = TweetData(self.db)
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
        self.mock_tweets = [Tweet(t) for t in self.tweets]

    def tearDown(self):
        os.remove(self.db)

    def test_file_creation(self):
        self.assertTrue(os.path.exists(self.db))

    def test_fields(self):
        f = self.feels_db.fields
        self.assertTrue(isinstance(f, tuple))
        self.assertTrue(len(f)>=11)

    def test_start(self):
        self.assertTrue(isinstance(self.feels_db.start, datetime))

    def test_dates(self):
        for t in self.mock_tweets:
            self.feels_db.insert_tweet(t)
        self.assertEqual(len(self.feels_db.tweet_dates), 3)

        tweets = []
        with open(self.tweets_data_path) as tweets_file:
            lines = filter(None, (line.rstrip() for line in tweets_file))
            for line in lines:
                try:
                    tweets.append(Tweet(json.loads(line)))
                except KeyError:
                    pass
        for t in tweets:
            self.feels_db.insert_tweet(t)
        self.assertEqual(len(self.feels_db.tweet_dates), 105)
        df = self.feels_db.tweet_dates
        timebox = timedelta(seconds=60)
        second = timedelta(seconds=1)
        df = df.groupby(pd.TimeGrouper(freq=f'{int(timebox/second)}S')).size()
        df = df[df != 0]
        print(df)
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[0], 103)

    def test_fetch(self):
        tweets = []
        with open(self.tweets_data_path) as tweets_file:
            lines = filter(None, (line.rstrip() for line in tweets_file))
            for line in lines:
                try:
                    tweets.append(Tweet(json.loads(line)))
                except KeyError:
                    pass
        for t in tweets:
            self.feels_db.insert_tweet(t)

        for t in self.mock_tweets:
            self.feels_db.insert_tweet(t)

        it = self.feels_db.fetchbin(binsize=timedelta(minutes=30))
        cur = next(it)
        self.assertEqual(cur[2]-cur[1], timedelta(minutes=30))
        self.assertEqual(len(cur[0]), 103)
        cur = next(it)
        self.assertEqual(len(cur[0]), 1)
        cur = next(it)
        self.assertEqual(len(cur[0]), 1)

    def test_data_operation(self):
        twt = {'created_at': 'Sun Feb 19 19:14:18 +0000 2017',
               'id_str': '833394296418082817',
               'text': 'All the feels!'}
        t = Tweet(twt)
        self.assertEqual(len(t.keys()), 7)
        self.feels_db.insert_tweet(t)
        df = self.feels_db.tweets_since(datetime.now())
        self.assertEqual(len(df), 0)
        df = self.feels_db.tweets_since(0)
        self.assertEqual(len(df), 1)
        df.sentiment = 0.9
        for row in df.itertuples():
            self.feels_db.update_tweet(
                {'id_str': row.id_str, 'sentiment': row.sentiment}
                )

        start = datetime(2017, 2, 17, 0, 0, 0)
        before = datetime(2017, 2, 18, 0, 0, 0)
        after = datetime(2017, 2, 20, 0, 0, 0)
        df = self.feels_db.tweets_between(start, before)
        self.assertEqual(len(df), 0)

        df = self.feels_db.tweets_between(start, after)
        self.assertEqual(len(df), 1)
