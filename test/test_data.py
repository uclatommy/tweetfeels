import unittest
from tweetfeels import TweetData
from tweetfeels import Tweet
from datetime import datetime
import json
import os


class Test_Data(unittest.TestCase):
    def setUp(self):
        self.tweets_data_path = 'test/sample.json'
        self.db = './test.sqlite'
        self.feels_db = TweetData(self.db)

    def tearDown(self):
        os.remove(self.db)

    def test_file_creation(self):
        self.assertTrue(os.path.exists(self.db))

    def test_fields(self):
        f = self.feels_db.fields
        self.assertTrue(isinstance(f, tuple))
        self.assertTrue(len(f)>=11)

    def test_scrub(self):
        data = {'a':1, 'b':2}
        scrubbed = self.feels_db.scrub(data)
        self.assertTrue(isinstance(scrubbed, str))

    def test_data_operation(self):
        twt = {'created_at': 'Sun Feb 19 19:14:18 +0000 2017',
               'id_str': '833394296418082817',
               'text': 'All the feels!'}
        t = Tweet(twt)
        self.assertEqual(len(t.keys()), 7)
        self.feels_db.insert_tweet(t)
        dfs = self.feels_db.tweets_since(datetime.now())
        for df in dfs:
            self.assertEqual(len(df), 0)
        dfs = self.feels_db.tweets_since(0)
        for df in dfs:
            self.assertEqual(len(df), 1)
            df.sentiment = 0.9
            for row in df.itertuples():
                self.feels_db.update_tweet(
                    {'id_str': row.id_str, 'sentiment': row.sentiment}
                    )
