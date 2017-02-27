#from distutils.core import setup
from setuptools import setup
import os

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = 'Real-time sentiment analysis for twitter.'

filename = 'tweetfeels/version.py'
exec(compile(open(filename, "rb").read(), filename, 'exec'))

setup(name='tweetfeels',
      version=__version__,
      description='Real-time sentiment analysis for twitter.',
      long_description=long_description,
      author='Thomas Chen',
      author_email='tkchen@gmail.com',
      url='https://github.com/uclatommy/tweetfeels',
      download_url='https://github.com/uclatommy/tweetfeels/tarball/{}'.format(
          __version__
          ),
      packages=['tweetfeels'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ],
      install_requires=[
          'tweepy', 'h5py', 'nltk', 'numpy', 'oauthlib', 'pandas',
          'python-dateutil', 'pytz', 'requests', 'requests-oauthlib',
          'six', 'twython'
          ],
      test_suite='nose.collector',
      tests_require=['nose']
     )
