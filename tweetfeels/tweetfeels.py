import time
from threading import Thread
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from re import sub
from tweepy import OAuthHandler
from tweepy import Stream
from tweetfeels import TweetData
from tweetfeels import TweetListener
import numpy as np


def clean(text):
    text = text.lower()
    text = sub("[0-9]+", "number", text)
    text = sub("#", "", text)
    text = sub("\\n", "", text)
    text = text.replace('$', '@')
    text = sub("@[^\\s]+", "", text)
    text = sub("(http|https)://[^\\s]*", "", text)
    text = sub("[^\\s]+@[^\\s]+", "", text)
    text = sub('[^a-z A-Z]+', '', text)
    return text


class TweetFeels(object):
    """
    The controller.

    :param credentials: A list of your 4 credential components.
    :param tracking: A list of keywords to track.
    :param db: A sqlite database to store data. Will be created if it doesn't
               already exist. Will append if it exists.
    :ivar calc_every_n: Wont calculate new sentiment until there are n records
                        in the queue.
    :ivar lang: A list of languages to include in tweet gathering.
    """
    _db_factory = (lambda db: TweetData(db))
    _auth_factory = (lambda cred: OAuthHandler(cred[0], cred[1]).set_access_token(cred[2], cred[3]))
    _listener_factory = (lambda ctrl: TweetListener(ctrl))
    _stream_factory = (lambda auth, listener: Stream(auth, listener))

    def __init__(self, credentials, tracking=[], db='feels.sqlite'):
        self._feels = TweetFeels._db_factory(db)
        _auth = TweetFeels._auth_factory(credentials)
        self._listener = TweetFeels._listener_factory(self)
        self._stream = TweetFeels._stream_factory(_auth, self._listener)
        self.tracking = tracking
        self.lang = ['en']
        self._sentiment = 0
        self._filter_level = 'low'
        self.calc_every_n = 10

    def start(self, seconds=None):
        def delayed_stop():
            time.sleep(seconds)
            print('Timer completed. Disconnecting now...')
            self.stop()

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

    def stop(self):
        self._stream.disconnect()

    def on_data(self, data):
        """
        Note: Due to upstream bug in tweepy for python3, it cannot handle the
        `filter_level` parameter in the `Stream.filter` function. Therefore,
        we'll take care of it here. The problem has been identified and fixed
        by the tweepy team here: https://github.com/tweepy/tweepy/pull/783
        """
        filter_value = {'none': 0, 'low': 1, 'medium': 2}
        value = filter_value[data['filter_level']]

        if value >= filter_value[self._filter_level]:
            self._feels.insert_tweet(data)

    def on_error(self, status):
        self.start()

    def _intensity(self, tweet):
        t = clean(tweet)
        return SentimentIntensityAnalyzer().polarity_scores(t)['compound']

    @property
    def sentiment(self):
        def avg_sentiment(df):
            avg = 0
            try:
                avg = np.average(
                    df.sentiment, weights=df.followers_count+df.friends_count
                    )
            except ZeroDivisionError:
                avg = 0
            return avg

        df = self._feels.queue
        if(len(df)>self.calc_every_n):
            df.sentiment = df.text.apply(self._intensity)
            for row in df.itertuples():
                self._feels.update_tweet(
                    {'id_str': row.id_str, 'sentiment': row.sentiment}
                    )
            df = df.loc[df.sentiment != 0]  # drop rows having 0 sentiment
            df = df.groupby('created_at')
            df = df.apply(avg_sentiment)
            df = df.sort_index()
            for row in df.iteritems():
                self._sentiment = self._sentiment*0.99 + row[1]*0.01
        return self._sentiment
