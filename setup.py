#from distutils.core import setup
from setuptools import setup

setup(name='tweetfeels',
      version='0.1.3',
      description='Real-time sentiment analysis for twitter.',
      author='Thomas Chen',
      author_email='tkchen@gmail.com',
      url='https://github.com/uclatommy/tweetfeels',
      download_url='https://github.com/uclatommy/tweetfeels/tarball/0.1.3',
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
      dependency_links=[
          'https://github.com/cjhutto/vaderSentiment/tarball/0.5'
          ],
      test_suite='nose.collector',
      tests_require=['nose']
     )
