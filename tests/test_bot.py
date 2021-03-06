# -*- coding: utf-8 -*-
"""
    unit test for PypiUpdatesBot
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
import mock
import pytest
import logbook


class DummyMemcache(object):
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data.update({key: value})

    def get(self, key):
        return self._data.get(key)


class DummyTweepyAPI(object):
    def update_status(self, message):
        pass


class TestPypiUpdatesBot(object):

    def _get_target_class(self):
        from pypi_updates import PypiUpdatesBot
        return PypiUpdatesBot

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_tweepy_api(self):
        target_obj = self._make_one()
        assert target_obj.tweepy_api is not None
        # same instance check
        assert target_obj.tweepy_api is target_obj.tweepy_api

    @mock.patch('pypi_updates.bot.pylibmc.Client',
                return_value=DummyMemcache())
    def test_memcache(self, mock_memcache):
        target_obj = self._make_one()
        assert target_obj.memcache is not None
        # same instance check
        assert target_obj.memcache is target_obj.memcache

    @mock.patch('pypi_updates.bot.feedparser.parse', return_value=None)
    def test_canot_parse_feed(self, mock):
        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        with logbook.TestHandler() as log_handler:
            update_status(target_obj)

        expected = [
            '[WARNING] [kuroko user]: Cannot parse RSS: {}'.format(RSS_URL)
        ]
        assert log_handler.formatted_records == expected
        mock.assert_called_with(RSS_URL)

    @mock.patch('pypi_updates.bot.feedparser.parse',
                return_value={'items': []})
    def test_canot_parse_items(self, mock):
        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        with logbook.TestHandler() as log_handler:
            update_status(target_obj)

        assert log_handler.formatted_records == [
            '[WARNING] [kuroko user]: Cannot parse RSS: {}'.format(RSS_URL)
        ]
        mock.assert_called_with(RSS_URL)

    @mock.patch('pypi_updates.bot.pylibmc.Client', return_value=DummyMemcache())
    @mock.patch('pypi_updates.bot.tweepy.API', return_value=DummyTweepyAPI())
    def test_update_status(self, mock_memcache, mock_tweepy):
        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': 'dummy',
                    'link': 'http://example.com/1/',
                    'description': 'dummydesc',
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
                {
                    'title': 'dummy2',
                    'link': 'http://example.com/2/',
                    'description': 'dummydesc2',
                    'published': '09 Oct 2014 15:18:59 GMT'
                },
            ]
        }

        m_parse = mock.patch('pypi_updates.bot.feedparser.parse',
                             return_value=dummy_feed)
        with logbook.TestHandler() as log_handler, m_parse as m:
            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009151858',
            u'[INFO] [kuroko user]: dummy http://example.com/1/',
            u'[INFO] [kuroko user]: dummy2 http://example.com/2/',
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153126'

    @mock.patch('pypi_updates.bot.tweepy.API', return_value=DummyTweepyAPI())
    def test_already_set_latest_published(self, mock_tweepy):

        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': 'dummy',
                    'link': 'http://example.com/1/',
                    'description': 'dummydesc',
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
                {
                    'title': 'dummy2',
                    'link': 'http://example.com/2/',
                    'description': 'dummydesc2',
                    'published': '09 Oct 2014 15:18:59 GMT'
                },
            ]
        }

        dummy_memcache = DummyMemcache()
        dummy_memcache.set('latest_published', '20141009151859')

        with logbook.TestHandler() as log_handler,\
                mock.patch('pypi_updates.bot.feedparser.parse',
                           return_value=dummy_feed) as m,\
                mock.patch('pypi_updates.bot.pylibmc.Client',
                           return_value=dummy_memcache):

            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009151859',
            u'[INFO] [kuroko user]: dummy http://example.com/1/',
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153126'

    def test_skip_old_tweet(self):
        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': 'dummy',
                    'link': 'http://example.com/1/',
                    'description': 'dummydesc',
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
            ]
        }

        dummy_memcache = DummyMemcache()
        dummy_memcache.set('latest_published', '20141009153126')

        with logbook.TestHandler() as log_handler,\
                mock.patch('pypi_updates.bot.feedparser.parse',
                           return_value=dummy_feed) as m,\
                mock.patch('pypi_updates.bot.pylibmc.Client',
                           return_value=dummy_memcache):

            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009153126',
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153126'

    @mock.patch('pypi_updates.bot.pylibmc.Client', return_value=DummyMemcache())
    @mock.patch('pypi_updates.bot.tweepy.API', return_value=DummyTweepyAPI())
    def test_tweet_over_length(self, mock_memcache, mock_tweepy):
        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': 'a' * 109,  # truncate
                    'link': 'http://example.com/1/',
                    'description': 'a' * 126,  # truncate
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
                {
                    'title': 'a' * 108,  # not truncate
                    'link': 'http://example.com/2/',
                    'description': 'a' * 125,  # not truncate
                    'published': '09 Oct 2014 15:18:59 GMT'
                },
            ]
        }

        with logbook.TestHandler() as log_handler,\
                mock.patch('pypi_updates.bot.feedparser.parse',
                           return_value=dummy_feed) as m:

            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009151858',
            u'[INFO] [kuroko user]: {}... http://example.com/1/'.format(u'a' * 105),
            u'[INFO] [kuroko user]: {} http://example.com/2/'.format(u'a' * 108),
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153126'

    @mock.patch('pypi_updates.bot.pylibmc.Client', return_value=DummyMemcache())
    def test_raise_tweepy_error(self, mock_memcache):
        from pypi_updates.bot import RSS_URL

        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': 'dummy',
                    'link': 'http://example.com/1/',
                    'description': 'dummydesc',
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
            ]
        }

        def _update_status_error(message):
            import tweepy
            raise tweepy.TweepError(reason='error')

        dummy_tweepy_api = DummyTweepyAPI()
        dummy_tweepy_api.update_status = _update_status_error

        with logbook.TestHandler() as log_handler,\
                mock.patch('pypi_updates.bot.feedparser.parse',
                           return_value=dummy_feed) as m,\
                mock.patch('pypi_updates.bot.tweepy.API',
                           return_value=dummy_tweepy_api):

            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009153125',
            u'[INFO] [kuroko user]: dummy http://example.com/1/',
            u'[ERROR] [kuroko user]: error'
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153125'

    @mock.patch('pypi_updates.bot.pylibmc.Client',
                return_value=DummyMemcache())
    @mock.patch('pypi_updates.bot.tweepy.API', return_value=DummyTweepyAPI())
    def test_multibyte_language(self, mock_memcache, mock_tweepy):

        from pypi_updates.bot import RSS_URL
        target_obj = self._make_one()
        update_status = target_obj.funcs[0]['options']['callback']

        dummy_feed = {
            'items': [
                {
                    'title': u'是假的數據',
                    'link': 'http://example.com/1/',
                    'description': u'是假的數據',
                    'published': '09 Oct 2014 15:31:26 GMT'
                },
            ]
        }

        m_parse = mock.patch('pypi_updates.bot.feedparser.parse',
                             return_value=dummy_feed)
        with logbook.TestHandler() as log_handler, m_parse as m:
            update_status(target_obj)

        assert log_handler.formatted_records == [
            u'[INFO] [kuroko user]: latest_published => 20141009153125',
            u'[INFO] [kuroko user]: 是假的數據 http://example.com/1/',
        ]
        m.assert_called_with(RSS_URL)
        assert target_obj.memcache.get('latest_published') == '20141009153126'


class TestIsValidMessage(object):

    def _call_fut(self, msg):
        from pypi_updates.bot import is_valid_message
        return is_valid_message(msg)

    @pytest.mark.parametrize('msg', [
        'new pypi packages',
    ])
    def test_valid_case(self, msg):
        assert self._call_fut(msg)

    @pytest.mark.parametrize('msg', [
        'kissanime',
        'new kissanime',
    ])
    def test_invalid_case(self, msg):
        assert not self._call_fut(msg)
