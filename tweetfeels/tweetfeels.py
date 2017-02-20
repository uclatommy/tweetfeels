import time
from threading import Thread
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from re import sub
from tweepy import OAuthHandler
from tweepy import Stream
from tweetfeels import TweetData
from tweetfeels import TweetListener


def clean(text):
    text = text.lower()
    text = sub("[0-9]+", "number", text)
    text = sub("#", "", text)
    text = sub("\n", "", text)
    text = text.replace('$', '@')
    text = sub("@[^\s]+", "", text)
    text = sub("(http|https)://[^\s]*", "", text)
    text = sub("[^\s]+@[^\s]+", "", text)
    text = sub('[^a-z A-Z]+', '', text)
    return text


class TweetFeels(object):
    """
    The controller.
    """
    def __init__(self, credentials, tracking=[], db='feels.sqlite'):
        self._listener = TweetListener(self.on_data, self.on_error)
        self._feels = TweetData(db)
        _auth = OAuthHandler(credentials[0], credentials[1])
        _auth.set_access_token(credentials[2], credentials[3])
        self._stream = Stream(_auth, self._listener)
        self.tracking = tracking
        self.lang = ['en']
        self._sentiment = 0

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
        if seconds is not None:
            t = Thread(target=delayed_stop)
            t.start()

    def stop(self):
        self._stream.disconnect()

    def on_data(self, data):
        self._feels.insert_tweet(data)

    def on_error(self, status):
        pass

    def _intensity(self, tweet):
        t = clean(tweet)
        return SentimentIntensityAnalyzer().polarity_scores(t)['compound']

    @property
    def sentiment(self):
        df = self._feels.queue
        if(len(df)>50):
            df.sentiment = df.text.apply(self._intensity)
            for row in df.itertuples():
                self._feels.update_tweet(
                    {'id_str': row.id_str, 'sentiment': row.sentiment}
                    )
            df = df.groupby(by=['created_at'], sort=True)['sentiment'].mean()
            for row in df.iteritems():
                self._sentiment = self._sentiment*0.99 + row[1]*0.01
        return self._sentiment
