from tweetfeels.utils import clean
from tweepy.streaming import StreamListener
from tweepy.utils import parse_datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import time


class Tweet(object):
    """
    Tweet object model. Access to tweet data works like a dict.

    :param data: A dict converted from json string representation of a tweet.
    """
    def __init__(self, data):
        self._data = data
        self._sentiment = None
        self._user_keys = (
            'followers_count', 'friends_count', 'location'
        )
        self._sentiment_keys = (
            'sentiment', 'pos', 'neu', 'neg'
        )
        try:
            ts = parse_datetime(data['created_at'])
            data['created_at'] = ts
        except KeyError:
            print(data)
            raise

    def __len__(self):
        return len(self.keys())

    def __contains__(self, other):
        return other in self.keys()

    def __getitem__(self, key):
        if key in self._user_keys:
            return self._data['user'][key]
        elif key in self._sentiment_keys:
            if key=='sentiment':
                return self.sentiment['compound']
            else:
                return self.sentiment[key]
        else:
            return self._data[key]

    def __str__(self):
        return str({k: self[k] for k in self.keys()})

    @property
    def sentiment(self):
        if self._sentiment is None:
            t = clean(self._data['text'])
            self._sentiment = SentimentIntensityAnalyzer().polarity_scores(t)
        return self._sentiment

    def keys(self):
        k = tuple(self._data.keys())
        k += self._sentiment_keys
        if 'user' in self._data:
            k += self._user_keys
        return k


class TweetListener(StreamListener):
    """
    Expects the controller to implement the handler methods.
    """
    def __init__(self, controller):
        self._controller = controller
        self.waited = 0

    def on_connect(self):
        self.waited = 0

    def on_data(self, data):
        dat = json.loads(data)
        if isinstance(dat, list):
            for d in dat:
                if 'created_at' in d:
                    twt = Tweet(d)
                    if hasattr(self._controller.on_data, '__call__'):
                        self._controller.on_data(twt)
                else:
                    continue
        else:
            if 'created_at' in dat:
                twt = Tweet(dat)
                if hasattr(self._controller.on_data, '__call__'):
                    self._controller.on_data(twt)
        return True

    def on_error(self, status):
        print(status)
        if self.waited == 0:
            if status == 420:
                self.waited = 60
            else:
                self.waited = 5
        self.reconnect_wait('exponential')

        if hasattr(self._controller.on_error, '__call__'):
            ret = self._controller.on_error(status)
        return True

    def reconnect_wait(self, pattern):
        if pattern == 'linear':
            time.sleep(self.waited)
            self.waited += 1
        elif pattern == 'exponential':
            time.sleep(self.waited)
            self.waited *= 2

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice
        Disconnect codes are listed here:
        https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
        """
        msg = json.loads(notice)['disconnect']
        if msg['code'] == 4 or msg['code'] > 8:
            self.reconnect_wait('linear')
            self._controller.start()
        else:
            print(f'Disconnected: {msg["code"]}: {msg["reason"]}')
