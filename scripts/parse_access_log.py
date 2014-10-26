# -*- coding: utf-8 -*-

# requires environment variable 'STATIC_BROWSER_SETTINGS' pointing to a
# config file with ACCESS_LOG and ACCESS_LOG_PICKLE

import pickle
import static_browser.web
import static_browser.parser

if __name__ == '__main__':
    access_log = static_browser.web.app.config['ACCESS_LOG']
    pickle_file = static_browser.web.app.config['ACCESS_LOG_PICKLE']
    parser = static_browser.parser.AccessLogParser(access_log)
    result = parser.parse()
    with open(pickle_file, 'w') as f:
        pickle.dump(result, f)
