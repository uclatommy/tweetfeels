from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import sqlite3
import time
from threading import Thread
import os


def make_feels_db(filename='feels.sqlite'):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    tbl_def = 'CREATE TABLE tweets(\
    id_str         CHARACTER(20)  PRIMARY KEY NOT NULL,\
    text           CHARACTER(140)             NOT NULL,\
    created_at     VARCHAR(50)                NOT NULL,\
    coordinates    VARCHAR(20),\
    favorite_count INTEGER,\
    favorited      VARCHAR(5),\
    lang           VARCHAR(10),\
    place          TEXT,\
    retweet_count  INTEGER,\
    source         TEXT\
    )'
    c.execute(tbl_def)
    conn.close()

class TweetListener(StreamListener):
    """
    A twitter streaming listener.
    """
    def __init__(self):
        self._db = 'feels.sqlite'
        if not os.path.isfile(self._db):
            make_feels_db(self._db)
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("select * from tweets")
        self.fields=tuple([f[0] for f in c.description])
        conn.close()

    def on_data(self, data):
        """
        Captures and writes data to database.
        """
        dat = json.loads(data)
        fields = str(tuple(self.fields))
        lst = [dat[f] for f in self.fields]
        for l in lst:
            if isinstance(l, dict):
                l = str(l)
        tup = tuple(lst)
        vals = '('
        vals = vals + '?,'*(len(tup)-1)
        vals = vals + '?)'
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        qry = f'INSERT OR IGNORE INTO tweets {fields} VALUES {vals}'
        try:
            c.execute(qry, tup)
        except:
            print(f'Failed Query: {qry}, {tup}')
        conn.commit()
        conn.close()
        return True

    def on_error(self, status):
        print(status)
        if status == 420:
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
        self.lang = ['en']

    def start(self, seconds=None):
        def delayed_stop():
            time.sleep(seconds)
            print('Timer completed. Disconnecting now...')
            self.stop()

        if len(self.tracking) == 0:
            print('Nothing to track!')
        else:
            self._stream.filter(track=self.tracking, languages=self.lang, async=True)
        if seconds is not None:
            t = Thread(target=delayed_stop)
            t.start()

    def stop(self):
        self._stream.disconnect()
