# static-browser

`static-browser` is a web interface for the resources hosted in the `static`
project on Wikimedia Tool Labs.

## Configuration

To use `static_browser`, you must set the environment variable `STATIC_BROWSER_SETTINGS` to
a point to a configuration file that contains the following entries:
 - `ACCESS_LOG`: the access log file to parse to check the file usage (required by
   `static_browser.parser.AccessLogParser`)
 - `ACCESS_LOG_PICKLE`: the file to write and read the results of the
   `static_browser.parser.AccessLogParser` to and from (required by `static_browser.web` and
   `static_browser.parser.AccessLogParser`)
 - `STATIC_PATH`: the path of the file containing the static resources (i. e. `static/res`;
   required by `static_browser.web`)
Optionally you can set `DEBUG` to `True` to run the `static_browser` web application in debug
mode.
