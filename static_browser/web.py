# coding=utf-8

import flask
import pickle
import static_browser.parser

app = flask.Flask('static_browser')
app.config.from_envvar('STATIC_BROWSER_SETTINGS')

@app.before_request
def before_request():
    flask.g.parser = static_browser.parser.NewPackageParser(app.config['STATIC_PATH'])

@app.context_processor
def context_processor_tools_static():
    def tools_static(package, version=None, file=None):
        path = '//tools-static.wmflabs.org/static/{0}/'.format(package)
        if version:
            path += version + '/'
            if file:
                path += file
        return path
    return dict(tools_static=tools_static)

@app.route('/')
def index():
    libraries = flask.g.parser.get_library_package_versions()
    fonts = flask.g.parser.get_font_package_versions()
    return flask.render_template('index.html', libraries=libraries, fonts=fonts)

@app.route('/show/<package>')
def show_package(package):
    package_description = flask.g.parser.get_package_description(package)
    if not package_description:
        flask.abort(404)
    versions = flask.g.parser.get_package_versions(package)
    if not versions:
        flask.abort(404)
    return flask.render_template('show_package.html', package=package_description, versions=versions)

@app.route('/show/<package>/<version>')
def show_package_version(package, version):
    package_description = flask.g.parser.get_package_version(package, version)
    if not package_description:
        flask.abort(404)
    all_files = flask.g.parser.get_all_files(package, version)
    with open(app.config['ACCESS_LOG_PICKLE']) as f:
        access = pickle.load(f)
    package_access = dict()
    if package in access and version in access[package]:
        package_access = access[package][version]
    return flask.render_template('show_package_version.html',
            package=package_description, access=package_access,
            all_files=all_files)

if __name__ == '__main__':
    app.run()
