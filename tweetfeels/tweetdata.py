import sqlite3
import os
import pandas as pd
import logging

class TweetData(object):
    """
    Abstraction of data store.
    """
    def __init__(self, file='feels.sqlite'):
        self._db = file
        if not os.path.isfile(self._db):
            self.make_feels_db(self._db)
        self._debug = False
        self.chunksize=1000

    @property
    def fields(self):
        conn = sqlite3.connect(self._db)
        c = conn.cursor()
        c.execute("select * from tweets")
        fields=tuple([f[0] for f in c.description])
        c.close()
        return fields

    def tweets_since(self, dt):
        conn = sqlite3.connect(self._db, detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql_query(
            'SELECT * FROM tweets WHERE created_at > ?', conn, params=(dt,),
            parse_dates=['created_at'], chunksize=self.chunksize
            )
        return df

    @property
    def all(self):
        conn = sqlite3.connect(self._db, detect_types=sqlite3.PARSE_DECLTYPES)
        df = pd.read_sql_query(
            'SELECT * FROM tweets', conn, parse_dates=['created_at'],
            chunksize=self.chunksize
            )
        return df

    def make_feels_db(self, filename='feels.sqlite'):
        conn = sqlite3.connect(filename)
        c = conn.cursor()
        tbl_def = 'CREATE TABLE tweets(\
        id_str          CHARACTER(20)  PRIMARY KEY NOT NULL,\
        text            CHARACTER(140)             NOT NULL,\
        created_at      timestamp                  NOT NULL,\
        coordinates     VARCHAR(20),\
        favorite_count  INTEGER,\
        favorited       VARCHAR(5),\
        lang            VARCHAR(10),\
        place           TEXT,\
        retweet_count   INTEGER,\
        source          TEXT,\
        friends_count   INTEGER,\
        followers_count INTEGER,\
        location        TEXT,\
        sentiment       DOUBLE                     NOT NULL,\
        pos             DOUBLE                     NOT NULL,\
        neu             DOUBLE                     NOT NULL,\
        neg             DOUBLE                     NOT NULL\
        )'
        c.execute(tbl_def)
        c.close()

    def scrub(self, item):
        if isinstance(item, dict):
            return str(item)
        else:
            return item

    def insert_tweet(self, tweet):
        keys = tuple([k for k in tweet.keys() if k in self.fields])
        vals = tuple([tweet[k] for k in keys])
        ins = '('
        ins = ins + '?,'*(len(vals)-1)
        ins = ins + '?)'
        qry = f'INSERT OR IGNORE INTO tweets {keys} VALUES {ins}'
        try:
            conn = sqlite3.connect(
                self._db, detect_types=sqlite3.PARSE_DECLTYPES
                )
            c = conn.cursor()
            c.execute(qry, vals)
            c.close()
            conn.commit()
        except:
            if self._debug:
                logging.warning(f'Failed Query: {qry}, {vals}')

    def update_tweet(self, tweet):
        id_str = tweet['id_str']
        buf = [k for k in tweet.keys() if k!='id_str']
        vals = tuple([tweet[k] for k in buf])
        updt = ''
        while len(buf) > 0:
            cur = buf.pop()
            if len(updt)>0:
                updt = updt + f',{cur}=?'
            else:
                updt = updt + f'{cur}=?'

        qry = f'UPDATE tweets SET {updt} WHERE id_str=?'
        try:
            conn = sqlite3.connect(
                self._db, detect_types=sqlite3.PARSE_DECLTYPES
                )
            c = conn.cursor()
            c.execute(qry, vals+(id_str,))
            c.close()
            conn.commit()
        except:
            if self._debug:
                logging.warning(f'Failed Query: {qry}, {vals+(id_str,)}')
