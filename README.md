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
Tweetfeels relies on [VADER sentiment analysis](https://github.com/cjhutto/vaderSentiment) to provide sentiment scores to user-defined topics. It does this by utilizing Twitter's streaming API to listen to real-time tweets around a particular topic.

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

## Example
```python

```
