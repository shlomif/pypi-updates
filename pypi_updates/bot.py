# -*- coding: utf-8 -*-
"""
    pypi_updates.bot
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Bot for PyPI Recent Updates

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
import feedparser
# import pylibmc
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
from six import print_

RSS_URL = 'https://pypi.org/rss/updates.xml'
TWEET_MAX_LENGTH = 130
ELIPSIS = '...'

NG_WORDS = [
    'kissanime',
]


def is_valid_message(msg):
    for ng_word in NG_WORDS:
        if ng_word in msg:
            return False
    return True


FILENAME = 'pypi-updates-smoker-cache.bin'


class MyCache:

    def get(self, key):
        try:
            with open(FILENAME, 'r') as fp:
                h = json.load(fp)
                if key not in h:
                    return None
                return h[key]
        except FileNotFoundError:
            pass
        return None

    def set(self, key, v):
        h = {}
        try:
            with open(FILENAME, 'r') as fp:
                h = json.load(fp)
        except FileNotFoundError:
            pass
        h[key] = v
        with open(FILENAME, 'w') as fp:
            json.dump(h, fp)
        return None

class PypiUpdatesBot:
    def __init__(self):
        self._memcache = MyCache()
        import logging
        self.log = logging.getLogger('pypi')

    @property
    def memcache(self):
        if hasattr(self, '_memcache'):
            return self._memcache
        self._memcache = '''pylibmc.Client(
            [os.getenv("MEMCACHIER_SERVERS")],
            username=os.getenv("MEMCACHIER_USERNAME"),
            password=os.getenv("MEMCACHIER_PASSWORD"),
            binary=True
        )'''
        return self._memcache

    def update_status(self):
        print('Start update status')
        rss = feedparser.parse(RSS_URL)
        # skip non feed items.
        if not rss or not rss['items']:
            msg = 'Cannot parse RSS: {}'.format(RSS_URL)
            self.log.warning(msg)
            print(msg)
            return

        latest_published = self.memcache.get('latest_published')
        if not latest_published:
            dt = parser.parse(rss['items'][-1]['published'])
            dt -= relativedelta(seconds=1)
            latest_published = dt.strftime('%Y%m%d%H%M%S')
            self.memcache.set('latest_published', latest_published)

        msg = 'latest_published => {}'.format(latest_published)
        self.log.info(msg)
        print(msg)
        tmp_latest = latest_published
        for item in rss['items']:
            published = parser.parse(
                item['published']
            ).strftime('%Y%m%d%H%M%S')

            # skip old feed.
            if int(published) <= int(latest_published):
                continue

            # shorten url
            url = item['link']

            # truncate description text.
            desc = item['description'].replace('\n', ' ')
            base = u"{}: {}".format(
                item['title'],
                desc
            )
            # tweet
            message = u'{} {}'.format(item['title'], item['link'])
            self.log.info(message)
            print_(message)
