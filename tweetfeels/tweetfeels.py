from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import sqlite3
import time
from threading import Thread


class TweetListener(StreamListener):
    """
    A twitter streaming listener.
    """
    def __init__(self):
        self._db = 'feels.sqlite'

    def on_data(self, data):
        """
        Captures and writes data to database.
        """
        dat = json.loads(data)
        for k,v in dat.items():
            print(f'{k}: {v}')
        return True

    def on_error(self, status):
        print(status)
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False


class TweetFeels(object):
    """
    The controller.
    """
    def __init__(self, credentials):
        _listener = TweetListener()
        _auth = OAuthHandler(credentials[0], credentials[1])
        _auth.set_access_token(credentials[2], credentials[3])
        self._stream = Stream(_auth, _listener)
        self.tracking = []

    def start(self, seconds=None):
        def sleeper():
            time.sleep(seconds)
            self.stop()

        if len(self.tracking) == 0:
            print('Nothing to track!')
        else:
            self._stream.filter(track=self.tracking, async=True)
        if seconds is not None:
            t = Thread(target=sleeper)
            t.start()

    def stop(self):
        self._stream.disconnect()
