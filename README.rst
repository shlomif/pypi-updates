==========================================
pypi-smoke-tester (work in progress)
==========================================

|travis| |coveralls| |requires|

Description
-----------------------------------------

* This aims to be the codebase for a pypi uploads smoke tester similar to
  https://en.wikipedia.org/wiki/CPAN#Testers for CPAN. It is still work
  in progress.
* The code is derived from that of https://github.com/tell-k/pypi-updates so
  thanks to them.


Plan:
-----

* Try to build and test the module inside a pristine forked snapshot of a
  https://en.wikipedia.org/wiki/Virtual_machine (for security)
* Decommission the snapshot after capturing the log.

Setup
-----------------------------------------

1. Clone repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 $ git clone git@github.com:tell-k/pypi-updates.git


2. Create ".env" file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 $ cd pypi-updates-bot
 $ toucn .env

Write your API tokens

::

 # .env file
 TWITTER_CONSUMER_KEY=[your consumer key]
 TWITTER_CONSUMER_SECRET=[your consumer secret]
 TWITTER_ACCESS_KEY=[your access key]
 TWITTER_ACCESS_SECRET=[your access secret]

3. Create heroku apps and settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 $ heroku login
 $ heroku apps:create pypi-updates
 $ heroku addons:add memcachier
 $ heroku plugins:install heroku-config
 $ heroku config:push

Confirm enviroment values.

::

 $ heroku config
 === xxxxxx-xxxxxx-xxxx Config Vars
 MEMCACHIER_PASSWORD:     xxxxxxxxxx
 MEMCACHIER_SERVERS:      xxx.xxx.xxx.xxxxxxx.xxxx:xxxxxx
 MEMCACHIER_USERNAME:     xxxxxxxx
 TWITTER_ACCESS_KEY:      xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 TWITTER_ACCESS_SECRET:   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 TWITTER_CONSUMER_KEY:    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 TWITTER_CONSUMER_SECRET: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

4. Deploy heroku apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 $ git push heroku master

 # Run the first time only
 $ heroku ps:scale bot=1

 # Confirm application log
 $ heroku logs --tail

Licence
-----------------------------------------

* MIT License
* See the LICENSE file for specific terms.


.. |travis| image:: https://travis-ci.org/tell-k/pypi-updates.svg?branch=master
    :target: https://travis-ci.org/tell-k/pypi-updates
    :alt: travis-ci.org

.. |coveralls| image:: https://coveralls.io/repos/tell-k/pypi-updates/badge.png
    :target: https://coveralls.io/r/tell-k/pypi-updates
    :alt: coveralls.io

.. |requires| image:: https://requires.io/github/tell-k/pypi-updates/requirements.svg?branch=master
     :target: https://requires.io/github/tell-k/pypi-updates/requirements/?branch=master
     :alt: requires.io
