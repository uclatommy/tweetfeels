import unittest
from unittest.mock import patch, MagicMock

from tweetfeels import TweetFeels


class Test_Feels(unittest.TestCase):
    def setUp(self):
        TweetFeels._db_factory = (lambda db: MagicMock())
        TweetFeels._auth_factory = (lambda cred: MagicMock())
        TweetFeels._listener_factory = (lambda ctrl: MagicMock())
        TweetFeels._stream_factory = (lambda auth, listener: MagicMock())

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
        data = {'filter_level': 'low', 'text': 'test data'}
        mock_feels.on_data(data)
        mock_feels._feels.insert_tweet.assert_called_once()

        mock_feels2 = TweetFeels("abcd")
        mock_feels2._filter_level = 'medium'
        mock_feels2.on_data(data)
        mock_feels2._feels.insert_tweet.assert_not_called()

    def test_intensity(self):
        mock_feels = TweetFeels("abcd")
        tweet = "tweetfeels is the shit!"
        self.assertTrue(mock_feels._intensity(tweet)>0)
