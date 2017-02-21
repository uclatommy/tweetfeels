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
## Introduction
Tweetfeels relies on [VADER sentiment analysis](https://github.com/cjhutto/vaderSentiment) to provide sentiment scores to user-defined topics. It does this by utilizing Twitter's streaming API to listen to real-time tweets around a particular topic. Some possible applications for this include:
* Calculating the social sentiment of particular political figures or issues and analyzing scores across geographic regions.
* Calculating sentiment scores for brands.
* Using collected social sentiment scores in an artificial intelligence algorithm to determine stock market buy and sell recommendations.
* And more!

## Install Methods
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

### Additional Requirements
1. You will need to obtain Twitter OAuth keys and supply them to tweetfeels in order to connect to Twitter's streaming API. Tweepy provides an excellent [tutorial](http://tweepy.readthedocs.io/en/v3.5.0/auth_tutorial.html#auth-tutorial) on how to obtain your keys.

2. Minimum python version of 3.6

## Examples
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

1. Stream tweets related to keyword "Trump" for 10 seconds, then calculate a sentiment score for the last 10 seconds.
    ```python
    >>> trump_feels = TweetFeels(login, tracking=['trump'])
    >>> trump_feels.start(10)
    Timer completed. Disconnecting now...
    >>> trump_feels.sentiment
    -0.0073007430343252711
    ```

2. Stream tweets continuously and print current sentiment score every 10 seconds
    ```python
    >>> from threading import Thread
    >>> import time
    >>>
    >>> def print_feels(seconds=10):
    ...     while go_on:
    ...         time.sleep(seconds)
    ...         print(f'[{time.ctime()}] Sentiment Score: {trump_feels.sentiment}')
    ...
    >>> go_on = True
    >>> t = Thread(target=print_feels)
    >>> trump_feels.start()
    >>> t.start()
    [Mon Feb 20 18:03:23 2017] Sentiment Score: -0.008372357248499813
    [Mon Feb 20 18:03:37 2017] Sentiment Score: -0.003758142966107373
    [Mon Feb 20 18:03:51 2017] Sentiment Score: -0.019303709913836925
    [Mon Feb 20 18:04:05 2017] Sentiment Score: -0.055019641398896174
    [Mon Feb 20 18:04:20 2017] Sentiment Score: -0.07207850963244739
    [Mon Feb 20 18:04:35 2017] Sentiment Score: -0.06494896516068921
    [Mon Feb 20 18:04:50 2017] Sentiment Score: -0.05696019326554382
    [Mon Feb 20 18:05:04 2017] Sentiment Score: -0.039204547830965976
    [Mon Feb 20 18:05:19 2017] Sentiment Score: -0.04412865418228736
    [Mon Feb 20 18:05:34 2017] Sentiment Score: -0.03692651001868575
    [Mon Feb 20 18:05:49 2017] Sentiment Score: -0.032870649707088036
    [Mon Feb 20 18:06:03 2017] Sentiment Score: -0.03195656229817732
    [Mon Feb 20 18:06:18 2017] Sentiment Score: -0.04804936912471804
    [Mon Feb 20 18:06:33 2017] Sentiment Score: -0.03265689149620199
    [Mon Feb 20 18:06:48 2017] Sentiment Score: -0.038081113973837975
    [Mon Feb 20 18:07:02 2017] Sentiment Score: -0.043703036700487634
    [Mon Feb 20 18:07:16 2017] Sentiment Score: -0.05497670144141494
    [Mon Feb 20 18:07:31 2017] Sentiment Score: -0.042350189513282524
    [Mon Feb 20 18:07:46 2017] Sentiment Score: -0.03235421754666877
    [Mon Feb 20 18:08:01 2017] Sentiment Score: -0.05711208717172596
    [Mon Feb 20 18:08:15 2017] Sentiment Score: -0.07458379173398412
    [Mon Feb 20 18:08:30 2017] Sentiment Score: -0.06876183464326659
    [Mon Feb 20 18:08:44 2017] Sentiment Score: -0.0649472552182835
    [Mon Feb 20 18:08:58 2017] Sentiment Score: -0.058314177602613836
    [Mon Feb 20 18:09:13 2017] Sentiment Score: -0.07502686422203823
    [Mon Feb 20 18:09:28 2017] Sentiment Score: -0.06267848788069674
    [Mon Feb 20 18:09:42 2017] Sentiment Score: -0.08114859672057512
    [Mon Feb 20 18:09:57 2017] Sentiment Score: -0.07412775442586042
    [Mon Feb 20 18:10:11 2017] Sentiment Score: -0.06577743915574097
    >>> trump_feels.stop()
    ```
    **Note:** Trump is an extremely high volume topic. We ran this for roughly 6.5 minutes and gathered nearly 15,000 tweets! For lower volume topics, you may want to poll the sentiment value less frequently than every 10 seconds.

3. Stream tweets continuously for another topic and save to a different database.
    ```python
    >>> tesla_feels = TweetFeels(login, tracking=['tesla', 'tsla', 'gigafactory', 'elonmusk'], db='tesla.sqlite')
    >>> tesla_feels.calc_every_n = 10
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

## Methodology
There are a multitude of ways in which you could combine hundreds or thousands of tweets across time in order to calculate a single sentiment score. One naive method might be to bin tweets into discretized time-boxes. For example, perhaps you average the individual sentiment scores every 10 seconds so that the current sentiment is the average over the last 10 seconds. In this method, your choice of discretization length is arbitrary and will have an impact on the perceived variance of the score. It also disregards any past sentiment calculations.

To correct for these effects, we time-box every second and do not discard the sentiment from prior calculations. Instead, we phase out older tweet sentiments geometrically as we add in new tweets:

![f1]

Where ![f2] is the aggregate sentiment at time t and ![f3] is the sentiment score for the current time-box. We start the calculation with ![f4], which is why you will see the sentiment score move away from zero until it stabilizes around the natural value. Within each time-box we are using a weighted average of sentiment scores. For each tweet, we utilize the associated user's follower count as the measure of influence.

Some tweets will also have a neutral score (0.0). In these cases, we exclude it from aggregation.

[f1]: http://chart.apis.google.com/chart?cht=tx&chl=S_{t}=0.99(S_{t-1})%2B0.01(s_t)
[f2]: http://chart.apis.google.com/chart?cht=tx&chl=S_t
[f3]: http://chart.apis.google.com/chart?cht=tx&chl=s_t
[f4]: http://chart.apis.google.com/chart?cht=tx&chl=S_0=0

### Caveats
The trained dataset that comes with [vaderSentiment](https://github.com/cjhutto/vaderSentiment) is optimized for social media, so it can the sentiment embedded in neologisms, internet shorthand, and even emoticons. However, it can only measure the aggregate sentiment value of a sentence or group of words. It does not measure whether or not a tweet agrees or disagrees with a particular ideology, political figure, or party. Although it is generally true that statements of disagreement will tend to have a negative sentiment. As an illustration, have a look at a few sentiment scores from the trump dataset:

| | Sentiment | Tweet |
| :---: | :--- | :--- |
| 1 | -0.5106 | RT @TEN_GOP: BREAKING: Massive riots happening now in Sweden. Stockholm in flames. Trump was right again! |
| 2 | -0.5574 | RT @Medeiros_____: Donald Trump and Russia @realDonaldTrump  #fakepresident  you're  fired |
| 3 | 0.3612 | RT @KamalaHarris: RT if you agree: Americans deserve a transparent, independent investigation into Russia’s involvement with the Trump camp. |
| 4 | 0.9217 | RT @robreiner: Someday, hopefully soon, Trump supporters will come to realize that he is not their president either. Freedom and justice fo… |

The first tweet is clearly voicing support for Donald Trump yet the content of the tweet produces a negative sentiment. The second tweet is clearly in opposition and it also produces negative sentiment. The fourth tweet is in opposition and produces an overwhelmingly positive sentiment. Clearly, sentiment scores should not be confused with ideological alignment! Don't even get me started on sarcastic tweets.

Sentiment scores tend to be more meaningful to non-ideological topics such as products and services. For example, here are some tweets from the Tesla dataset:

| | Sentiment | Tweet |
| :---: | :--- | :--- |
| 1 | -0.296 | Tesla is ‘illegally selling cars’ in Connecticut, says Dealership Association as they try to stop direct-sale bill |
| 2 | -0.5859 | Supercharger Realtime Availability Map is offline until further notice. I am no longer receiving data as Tesla asked for it to be cut off. |
| 3 | 0.5859 | Elon Musk Steps Forward To Help Tesla Driver Who Sacrificed Car To Save Stroke Victim via @aplusapp |
| 4 | 0.4404 | RT @ElectrekCo: Tesla Model 3: aluminum part supplier announces investment to increase output ahead of Model 3 production…  |
