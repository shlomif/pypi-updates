#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 shlomif <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.

"""

"""

import time
from pypi_updates.bot import PypiUpdatesBot

bot = PypiUpdatesBot()
while True:
    bot.update_status()
    time.sleep(60)
