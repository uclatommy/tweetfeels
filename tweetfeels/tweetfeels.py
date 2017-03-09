import time
from datetime import datetime, timedelta
from threading import Thread
from collections import deque
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np

from tweepy import (OAuthHandler,
                    Stream)
from tweetfeels import (TweetData,
                        TweetListener)
from tweetfeels.utils import clean


class TweetFeels(object):
    """
    The controller.

    :param credentials: A list of your 4 credential components.
    :param tracking: A list of keywords to track.
    :param db: A sqlite database to store data. Will be created if it doesn't
               already exist. Will append if it exists.
    :ivar lang: A list of languages to include in tweet gathering.
    :ivar buffer_limit: When the number of tweets in the buffer hits this limit
                        all tweets in the buffer gets flushed to the database.
    :ivar connected: Tells you if TweetFeels is connected and listening to
                     Twitter.
    :ivar sentiment: The real-time sentiment score.
    :ivar binsize: The fixed observation interval between new sentiment
                   calculations. (default = 60 seconds)
    :ivar factor: The fall-off factor used in real-time sentiment calculation.
                  (default = 0.99)
    """
    _db_factory = (lambda db: TweetData(db))
    _listener_factory = (lambda ctrl: TweetListener(ctrl))
    _stream_factory = (lambda auth, listener: Stream(auth, listener))

    def __init__(self, credentials, tracking=[], db='feels.sqlite'):
        self._feels = TweetFeels._db_factory(db)
        _auth = OAuthHandler(credentials[0], credentials[1])
        _auth.set_access_token(credentials[2], credentials[3])
        self._listener = TweetFeels._listener_factory(self)
        self._stream = TweetFeels._stream_factory(_auth, self._listener)
        self.tracking = tracking
        self.lang = ['en']
        self._sentiment = 0
        self._filter_level = 'low'
        self._bin_size = timedelta(seconds=60)
        self._latest_calc = self._feels.start
        self._tweet_buffer = deque()
        self.buffer_limit = 50
        self._factor = 0.99

    @property
    def binsize(self):
        return self._bin_size

    @binsize.setter
    def binsize(self, value):
        assert(isinstance(value, timedelta))
        if value != self._bin_size:
            self._latest_calc = self._feels.start
        self._bin_size = value

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, value):
        assert(value<=1 and value>0)
        self._latest_calc = self._feels.start
        self._factor = value

    @property
    def connected(self):
        return self._stream.running

    @property
    def sentiment(self):
        end = self._feels.end
        sentiments = self.sentiments(
            strt=self._latest_calc, end=end, delta_time=self._bin_size
            )
        ret = None
        for s in sentiments:
            ret = s
        return ret

    def start(self, seconds=None, selfupdate=60):
        """
        Start listening to the stream.

        :param seconds: If you want to automatically disconnect after a certain
                        amount of time, pass the number of seconds into this
                        parameter.
        :param selfupdate: Number of seconds between auto-calculate.
        """
        def delayed_stop():
            time.sleep(seconds)
            print('Timer completed. Disconnecting now...')
            self.stop()

        def self_update():
            while self.connected:
                time.sleep(selfupdate)
                self.sentiment

        if len(self.tracking) == 0:
            print('Nothing to track!')
        else:
            self._stream.filter(
                track=self.tracking, languages=self.lang, async=True
                )
#  This does not work due to upstream bug in tweepy 3.5.0. They have fixed it in
#  https://github.com/tweepy/tweepy/pull/783
#            self._stream.filter(
#               track=self.tracking, languages=self.lang, async=True,
#               filter_level=self._filter_level
#               )
        if seconds is not None:
            t = Thread(target=delayed_stop)
            t.start()

        if selfupdate is not None and selfupdate > 0:
            t2 = Thread(target=self_update)
            t2.start()

    def stop(self):
        """
        Disconnect from the stream.

        Warning: Connecting and disconnecting too frequently will get you
        blacklisted by Twitter. Your connections should be long-lived.
        """
        self._stream.disconnect()

    def on_data(self, data):
        """
        Called by :class:`TweetListener` when new tweet data is recieved.

        Note: Due to upstream bug in tweepy for python3, it cannot handle the
        `filter_level` parameter in the `Stream.filter` function. Therefore,
        we'll take care of it here. The problem has been identified and fixed
        by the tweepy team here: https://github.com/tweepy/tweepy/pull/783

        :param data: The tweet data. Should be a single :class:`Tweet`.
        :type data: Tweet
        """
        filter_value = {'none': 0, 'low': 1, 'medium': 2}
        value = filter_value[data['filter_level']]

        if value >= filter_value[self._filter_level]:
            self._tweet_buffer.append(data)

            if len(self._tweet_buffer) > self.buffer_limit:
                t = Thread(target=self.clear_buffer)
                t.start()

    def clear_buffer(self):
        """
        Pops all the tweets currently in the buffer and puts them into the db.
        """
        while True:
            try:
                # The insert calculates sentiment values
                self._feels.insert_tweet(self._tweet_buffer.popleft())
            except IndexError:
                break

    def on_error(self, status):
        """
        Called by :class:`TweetListener` when an error is recieved.
        """
        self.start()

    def sentiments(self, strt=None, end=None, delta_time=None):
        """
        Provides a generator for sentiment values in ``delta_time`` increments.

        :param start: The start time at which the generator yeilds a value. If
                      not provided, generator will start from beginning of your
                      dataset.
        :type start: datetime
        :param end: The ending datetime of the series. If not provided,
                    generator will not stop until it reaches the end of your
                    dataset.
        :type end: datetime
        :param delta_time: The time length that each sentiment value represents.
                           If not provided, the generator will use the setting
                           configured by :class:`TweetFeels`.
        :type delta_time: timedelta
        """
        beginning = self._feels.start

        if strt is None:
            self._latest_calc = beginning
            strt = beginning
        else:
            self._latest_calc = max(strt, self._feels.start)
        if end is None:
            end = self._feels.end
        if delta_time is None:
            delta_time = self._bin_size

        # get to the starting point
        if strt < self._latest_calc:
            self._sentiment = 0
            df = self._feels.tweets_between(beginning, strt)
        else:
            df = self._feels.tweets_between(self._latest_calc, strt)

        self._sentiment = self.model_sentiment(
            df, self._sentiment, self._factor
            )
        self._latest_calc = strt

        # start yielding sentiment values
        end = min(end, self._feels.end)
        if self._latest_calc < end:
            dfs = self._feels.fetchbin(
                start=self._latest_calc, end=end, binsize=delta_time
                )
            sentiment = deque()
            for df in dfs:
                try:
                    # only save sentiment value if not the last element
                    self._sentiment = sentiment.popleft()
                except IndexError:
                    pass

                sentiment.append(
                    self.model_sentiment(df[0], self._sentiment, self._factor)
                    )
                self._latest_calc = df[1]
                # Yield the latest element
                yield sentiment[-1]
        else:
            # this only happens when strt >= end
            yield self._sentiment

    def model_sentiment(self, df, s, fo=0.99):
        """
        Defines the real-time sentiment model given a dataframe of tweets.

        :param df: A tweets dataframe.
        :param s: The initial sentiment value to begin calculation.
        :param fo: Fall-off factor
        """
        df = df.loc[df.sentiment != 0]  # drop rows having 0 sentiment
        if(len(df)>0):
            try:
                val = np.average(
                    df.sentiment, weights=df.followers_count+df.friends_count
                    )
            except ZeroDivisionError:
                val = 0
            s = s*fo + val*(1-fo)
        return s
