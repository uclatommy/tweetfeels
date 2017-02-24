import unittest
from unittest.mock import patch

from tweetfeels import TweetFeels


class Test_Feels(unittest.TestCase):
    def setUp(self):
        TweetFeels._db_factory = (lambda db: print(db))
        TweetFeels._auth_factory = (lambda cred: print(cred))
        TweetFeels._listener_factory = (lambda ctrl: print(ctrl))
        TweetFeels._stream_factory = (lambda auth, listener: print(auth))

    def test_start(self):
        mock_feels = TweetFeels("abcd")
