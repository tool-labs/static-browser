# coding=utf-8

import flask
import pickle
import static_browser.parser

app = flask.Flask('static_browser')
app.config.from_envvar('STATIC_BROWSER_SETTINGS')

@app.before_request
def before_request():
    flask.g.parser = static_browser.parser.PackageParser(app.config['STATIC_PATH'])

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

@app.route('/show/<package>')
def show_package(package):
    package_description = flask.g.parser.parse_package(package)
    if not package_description or not 'title' in package_description:
        flask.abort(404)
    package_description['name'] = package
    return flask.render_template('show_package.html', package=package_description)

@app.route('/show/<package>/<version>')
def show_version(package, version):
    package_description = flask.g.parser.parse_version(package, version)
    if not package_description:
        flask.abort(404)
    package_description['name'] = package
    package_description['version'] = version
    all_files = flask.g.parser.get_all_files(package, version)
    with open(app.config['ACCESS_LOG_PICKLE']) as f:
        access = pickle.load(f)
    package_access = dict()
    if package in access and version in access[package]:
        package_access = access[package][version]
    return flask.render_template('show_version.html',
            package=package_description, access=package_access,
            all_files=all_files)

if __name__ == '__main__':
    app.run()
