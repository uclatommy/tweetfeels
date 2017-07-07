<image src="https://uclatommy.github.io/tweetfeels/images/tweetfeels.svg" width="100%" height="180">
<p align="center">
<a href="https://travis-ci.org/uclatommy/tweetfeels">
    <image src="https://travis-ci.org/uclatommy/tweetfeels.svg?branch=master">
</a>
<a href="https://github.com/uclatommy/tweetfeels/issues">
     <img src="https://img.shields.io/github/issues/uclatommy/tweetfeels.svg">
</a>
<a href="https://www.python.org/">
     <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg">
</a>
<a href="https://www.clahub.com/agreements/uclatommy/tweetfeels">
     <img src="https://img.shields.io/badge/CLA-open-brightgreen.svg">
</a>
</p>

# Introduction
Tweetfeels relies on [VADER sentiment analysis](https://github.com/cjhutto/vaderSentiment) to provide sentiment scores to user-defined topics. It does this by utilizing Twitter's streaming API to listen to real-time tweets around a particular topic. Some possible applications for this include:
* Calculating the social sentiment of particular political figures or issues and analyzing scores across geographic regions.
* Calculating sentiment scores for brands.
* Using sentiment scores as training features for a learning algorithm to determine stock buy and sell triggers.
* And more!

# Install Methods
1. The easiest way is to install from PyPI:
    ```
    > pip3 install tweetfeels
    ```

2. If you've installed from PyPI and want to upgrade:
    ```
    > pip3 install --upgrade tweetfeels
    ```

3. You can also install by cloning this repo:
    ```
    > git clone https://github.com/uclatommy/tweetfeels.git
    > cd tweetfeels
    > python3 setup.py install
    ```

## Additional Requirements
1. You will need to obtain Twitter OAuth keys and supply them to tweetfeels in order to connect to Twitter's streaming API. Go [here](https://twittercommunity.com/t/how-to-get-my-api-key/7033) for instructions on how to obtain your keys.

2. Minimum python version of 3.6

3. If for some reason pip did not install the vader lexicon:
    ```
    > python3 -m nltk.downloader vader_lexicon
    ```

# Examples
*Note: Authorization keys in the examples are masked for privacy.*

For all examples, we use a few common boilerplate lines:
```python
from tweetfeels import TweetFeels

consumer_key = '*************************'
consumer_secret = '**************************************************'
access_token = '**************************************************'
access_token_secret = '*********************************************'
login = [consumer_key, consumer_secret, access_token, access_token_secret]
```

#### Stream tweets related to keyword "Trump" for 10 seconds, then calculate a sentiment score for the last 10 seconds.
```python
>>> trump_feels = TweetFeels(login, tracking=['trump'])
>>> trump_feels.start(10)
Timer completed. Disconnecting now...
>>> trump_feels.sentiment.value
-0.0073007430343252711
```

#### Stream tweets continuously and print current sentiment score every 10 seconds
```python
>>> from threading import Thread
>>> import time
>>>
>>> def print_feels(seconds=10):
...     while go_on:
...         time.sleep(seconds)
...         print(f'[{time.ctime()}] Sentiment Score: {trump_feels.sentiment.value}')
...
>>> go_on = True
>>> t = Thread(target=print_feels)
>>> trump_feels.start()
>>> t.start()
[Mon Feb 20 23:42:02 2017] Sentiment Score: -0.010528112416665309
[Mon Feb 20 23:42:13 2017] Sentiment Score: -0.007496043169013409
[Mon Feb 20 23:42:25 2017] Sentiment Score: -0.015294713038619036
[Mon Feb 20 23:42:36 2017] Sentiment Score: -0.030362951884842962
[Mon Feb 20 23:42:48 2017] Sentiment Score: -0.042087318872206333
[Mon Feb 20 23:42:59 2017] Sentiment Score: -0.041308681936680865
[Mon Feb 20 23:43:10 2017] Sentiment Score: -0.056203371039128994
[Mon Feb 20 23:43:22 2017] Sentiment Score: -0.07374769163753854
[Mon Feb 20 23:43:34 2017] Sentiment Score: -0.09549338153348486
[Mon Feb 20 23:43:46 2017] Sentiment Score: -0.10943157911799692
[Mon Feb 20 23:43:57 2017] Sentiment Score: -0.1406756546353098
[Mon Feb 20 23:44:08 2017] Sentiment Score: -0.12366467180485821
[Mon Feb 20 23:44:20 2017] Sentiment Score: -0.14460675229624026
[Mon Feb 20 23:44:32 2017] Sentiment Score: -0.13149386547613803
[Mon Feb 20 23:44:43 2017] Sentiment Score: -0.14568801433828418
[Mon Feb 20 23:44:55 2017] Sentiment Score: -0.14505295656838593
[Mon Feb 20 23:45:06 2017] Sentiment Score: -0.12853750933261338
[Mon Feb 20 23:45:17 2017] Sentiment Score: -0.11649611157554504
[Mon Feb 20 23:45:29 2017] Sentiment Score: -0.11382260762980569
[Mon Feb 20 23:45:40 2017] Sentiment Score: -0.11121839471955856
[Mon Feb 20 23:45:52 2017] Sentiment Score: -0.11083390577340985
[Mon Feb 20 23:46:03 2017] Sentiment Score: -0.10879727669948112
[Mon Feb 20 23:46:15 2017] Sentiment Score: -0.10137079133168492
[Mon Feb 20 23:46:26 2017] Sentiment Score: -0.10075971619875508
[Mon Feb 20 23:46:38 2017] Sentiment Score: -0.1194907722483259
[Mon Feb 20 23:46:49 2017] Sentiment Score: -0.1328795394197093
[Mon Feb 20 23:47:01 2017] Sentiment Score: -0.13734346200202507
[Mon Feb 20 23:47:12 2017] Sentiment Score: -0.1157629833027525
[Mon Feb 20 23:47:24 2017] Sentiment Score: -0.11030256885649424
[Mon Feb 20 23:47:35 2017] Sentiment Score: -0.12185876174059834
[Mon Feb 20 23:47:47 2017] Sentiment Score: -0.11323251979604802
[Mon Feb 20 23:47:58 2017] Sentiment Score: -0.11307793897469191
>>> trump_feels.stop()
```

**Note:** Trump is an extremely high volume topic. We ran this for roughly 6 minutes and gathered nearly 15,000 tweets! For lower volume topics, you may want to poll the sentiment value less frequently than every 10 seconds.

#### Stream tweets continuously for another topic and save to a different database.

```python
>>> tesla_feels = TweetFeels(login, tracking=['tesla', 'tsla', 'gigafactory', 'elonmusk'], db='tesla.sqlite')
>>> t = Thread(target=print_feels, args=(tesla_feels, 120))
>>> tesla_feels.start()
>>> t.start()
[Mon Feb 20 17:39:15 2017] Sentiment Score: 0.03347735418362685
[Mon Feb 20 17:41:15 2017] Sentiment Score: 0.09408120307200825
[Mon Feb 20 17:43:15 2017] Sentiment Score: 0.12554072120979093
[Mon Feb 20 17:45:16 2017] Sentiment Score: 0.12381491277579157
[Mon Feb 20 17:47:16 2017] Sentiment Score: 0.17121666657137832
[Mon Feb 20 17:49:16 2017] Sentiment Score: 0.22588283902409384
[Mon Feb 20 17:51:16 2017] Sentiment Score: 0.23587583668725887
[Mon Feb 20 17:53:16 2017] Sentiment Score: 0.2485916177213093
```

#### Use the sentiments generator to replay captured data and plot
```python
import pandas as pd
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
data1 = {s.end: s.value for s in tesla_feels.sentiments(delta_time=timedelta(minutes=15), nans=True)}
data2 = {s.end: s.volume for s in tesla_feels.sentiments(delta_time=timedelta(minutes=15), nans=True)}
df1 = pd.DataFrame.from_dict(data1, orient='index')
df2 = pd.DataFrame.from_dict(data2, orient='index')
fig, axes = plt.subplots(nrows=2, ncols=1)
fig.set_size_inches(15, 5)
plt.subplot(211).axes.get_xaxis().set_visible(False)
df1[0].plot(kind='line', title='Tesla Sentiment')
plt.subplot(212)
df2[0].plot(kind='area', title='Volume')
```
<image src="https://uclatommy.github.io/tweetfeels/images/volume.svg" width="100%" height="300">

# Methodology
There are a multitude of ways in which you could combine hundreds or thousands of tweets across time in order to calculate a single sentiment score. One naive method might be to bin tweets into discretized time-boxes. For example, perhaps you average the individual sentiment scores every 10 seconds so that the current sentiment is the average over the last 10 seconds. In this method, your choice of discretization length is arbitrary and will have an impact on the perceived variance of the score. It also disregards any past sentiment calculations.

To correct for these effects, we time-box every minute by default and do not discard the sentiment from prior calculations. Instead, we phase out older tweet sentiments geometrically as we add in new tweets:

![f1]

Where ![f2] is the aggregate sentiment at time t, ![f3] is the sentiment score for the current time-box, and ![f5] is the fall-off factor between 0 and 1. We start the calculation with ![f4], which is why you will see the sentiment score move away from zero until it stabilizes around the natural value. Within each time-box we are using a weighted average of sentiment scores. For each tweet, we utilize the associated user's followers and friends count as the measure of influence.

Some tweets will also have a neutral score (0.0). In these cases, we exclude it from aggregation.

Here's an example of different model parameterizations of real-time Tesla sentiment:
<image src="https://uclatommy.github.io/tweetfeels/images/tesla-sentiment.svg" width="100%" height="300">

[f1]: http://chart.apis.google.com/chart?cht=tx&chl=S_{t}=%5calpha{S_{t-1}}%2B(1-%5calpha)s_t
[f2]: http://chart.apis.google.com/chart?cht=tx&chl=S_t
[f3]: http://chart.apis.google.com/chart?cht=tx&chl=s_t
[f4]: http://chart.apis.google.com/chart?cht=tx&chl=S_0=0
[f5]: http://chart.apis.google.com/chart?cht=tx&chl=%5calpha

## Caveats
The trained dataset that comes with [vaderSentiment](https://github.com/cjhutto/vaderSentiment) is optimized for social media, so it can recognize the sentiment embedded in neologisms, internet shorthand, and even emoticons. However, it can only measure the aggregate sentiment value of a sentence or group of words. It does not measure whether or not a tweet agrees or disagrees with a particular ideology, political figure, or party. Although it is generally true that statements of disagreement will tend to have a negative sentiment. As an illustration, have a look at a few sentiment scores from the trump dataset:

| | Sentiment | Tweet |
| :---: | :--- | :--- |
| 1 | -0.5106 | RT @TEN_GOP: BREAKING: Massive riots happening now in Sweden. Stockholm in flames. Trump was right again! |
| 2 | -0.8744 | RT @kurteichenwald: Intel shows our ally, Sweden, has no rise in crime. Trump saw on Fox it does. So he ignores intel, attacks our ally. ht… |
| 3 | 0.7003 | RT @NoBoomGaming: I'm a glass half full kind of guy. Now that Trump won, think of all the new memes we'll have over the next four years! |
| 4 | 0.6249 | RT @SandraTXAS: Nikki Haley is kicking a$$ at the UN👊💥💥 Trump made a great choice for envoy to the UN!! #Israel #MAGA |

The first tweet is clearly voicing support for Donald Trump yet we get a negative score. The second tweet is clearly in opposition and it also produces a very negative sentiment. The fourth tweet is a case of sentiment aligning with approval. Clearly, sentiment scores should not be confused with ideological alignment or approval because it can go both ways! You can approve and make a negative comment and you can disapprove and make a positive sounding comment! Don't even get me started on sarcastic tweets (see third one).

Sentiment scores tend to be more meaningful to non-ideological topics such as products and services. For example, here are some tweets from the Tesla dataset:

| | Sentiment | Tweet |
| :---: | :--- | :--- |
| 1 | -0.296 | Tesla is ‘illegally selling cars’ in Connecticut, says Dealership Association as they try to stop direct-sale bill |
| 2 | -0.5859 | Supercharger Realtime Availability Map is offline until further notice. I am no longer receiving data as Tesla asked for it to be cut off. |
| 3 | 0.5859 | Elon Musk Steps Forward To Help Tesla Driver Who Sacrificed Car To Save Stroke Victim via @aplusapp |
| 4 | 0.4404 | RT @ElectrekCo: Tesla Model 3: aluminum part supplier announces investment to increase output ahead of Model 3 production…  |
