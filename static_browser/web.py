# coding=utf-8

import flask
import static_browser.parser

app = flask.Flask('static_browser')
app.config.from_envvar('STATIC_BROWSER_SETTINGS')

@app.before_request
def before_request():
    flask.g.parser = static_browser.parser.PackageParser('/data/local/Programme/static/res/')

@app.context_processor
def context_processor_tools_static():
    def tools_static(package, version=None, file=None):
        path = '//tools.wmflabs.org/static/res/{0}/'.format(package)
        if version:
            path += version + '/'
            if file:
                path += file
        return path
    return dict(tools_static=tools_static)

@app.route('/')
def index():
    packages = flask.g.parser.parse()
    return flask.render_template('index.html', packages=packages)
