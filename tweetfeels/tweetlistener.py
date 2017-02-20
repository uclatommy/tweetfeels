from tweepy.streaming import StreamListener
import json
import time


class Tweet(object):
    """
    Tweet object model.
    """
    def __init__(self, data):
        self._data = data
        self._user_keys = (
            'followers_count', 'friends_count', 'location'
        )
        try:
            ts = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                )
            data['created_at'] = str(ts)
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
        else:
            return self._data[key]

    def keys(self):
        k = tuple(self._data.keys())
        if 'user' in self._data:
            k += self._user_keys
        return k


class TweetListener(StreamListener):
    def __init__(self, on_data, on_error):
        self._on_data = on_data
        self._on_error = on_error

    def on_data(self, data):
        dat = json.loads(data)
        if isinstance(dat, list):
            for d in dat:
                if 'created_at' in d:
                    twt = Tweet(d)
                    if hasattr(self._on_data, '__call__'):
                        self._on_data(twt)
                else:
                    continue
        else:
            if 'created_at' in dat:
                twt = Tweet(dat)
                if hasattr(self._on_data, '__call__'):
                    self._on_data(twt)
        return True

    def on_error(self, status):
        print(status)
        ret = True
        if hasattr(self._on_error, '__call__'):
            ret = self._on_error(status)
        if status == 420:
            #returning False in on_data disconnects the stream
            return False
        return ret
