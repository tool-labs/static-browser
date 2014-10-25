# coding=utf-8

import distutils.core

with open('requirements.txt') as f:
    reqs = f.read().splitlines()

distutils.core.setup(
    name='static-browser',
    version='0.1dev',
    author='Robin Krahl',
    author_email='robin.krahl@wikipedia.de',
    packages=['static_browser'],
    package_data={'righttovote': ['templates/*.html', 'static/js/*.js',
            'static/css/*.css']},
    license='LICENSE',
    long_description=open('README.md').read(),
    install_requires=reqs,
)
