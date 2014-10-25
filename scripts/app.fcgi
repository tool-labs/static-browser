#! /data/project/static-browser/bin/python
# -*- coding: utf-8 -*-

import flup.server.fcgi
import logging
import os

os.environ['STATIC_BROWSER_SETTINGS'] = '/data/project/static-browser/app.cfg'

import static_browser.web

handler = logging.FileHandler('/data/project/static-browser/error.log')
static_browser.app.logger.setLevel(logging.DEBUG)
static_browser.app.logger.addHandler(handler)

if __name__ == '__main__':
    flup.server.fcgi.WSGIServer(static_browser.web.app).run()
