# coding=utf-8

import datetime
import json
import logging
import os
import os.path
import re
import sets

class PackageParser:
    DESCRIPTION_FILE = 'index.json'
    KEY_TITLE = 'title'
    KEY_LICENSE = 'license'
    KEY_LICENSE_FILE = 'license-file'
    KEY_FILES = 'files'
    KEY_DESCRIPTION = 'description'
    REQUIRED_KEYS = [KEY_TITLE, KEY_LICENSE, KEY_LICENSE_FILE, KEY_FILES]

    def __init__(self, path, logger=logging.getLogger(__name__)):
        self.path = path
        self.logger = logger

    def get_packages(self):
        packages = []
        for item in os.listdir(self.path):
            self.logger.debug(' * Checking {0}'.format(item))
            if os.path.isdir(os.path.join(self.path, item)):
                self.logger.debug('   - added to the package list')
                packages.append(item)
            else:
                self.logger.debug('   - not a directory')
        return packages

    def get_versions(self, package):
        versions = []
        path = os.path.join(self.path, package)
        for item in os.listdir(path):
            self.logger.debug(' * Checking {0}/{1}'.format(package, item))
            if os.path.isdir(os.path.join(path, item)):
                self.logger.debug('   - added to the version list')
                versions.append(item)
            else:
                self.logger.debug('   - not a directory')
        return versions

    def get_description_path(self, package, version):
        path = os.path.join(self.path, package)
        if version is not None:
            path = os.path.join(path, version)
        return os.path.join(path, PackageParser.DESCRIPTION_FILE)

    def parse_description(self, package, version=None):
        path = self.get_description_path(package, version)
        self.logger.debug(' * Parsing description file {0}'.format(path))
        if not os.path.isfile(path):
            return dict()
        try:
            with open(path) as f:
                self.logger.debug('   - parsing')
                return json.load(f)
        except:
            self.logger.debug('   - failed')
            return dict()

    def validate_description(self, description):
        valid = True
        for key in PackageParser.REQUIRED_KEYS:
            valid = valid and key in description and description[key]
        return valid

    def parse(self):
        result = dict()
        packages = self.get_packages()
        for package in packages:
            package_description = self.parse_description(package)
            versions = self.get_versions(package)
            for version in versions:
                version_description = self.parse_description(package, version)
                for key, value in package_description.iteritems():
                    version_description.setdefault(key, value)
                if self.validate_description(version_description):
                    self.logger.debug(' * Registering package {0}/{1}'.format(package, version))
                    if not package in result:
                        result[package] = dict()
                    result[package][version] = version_description
                else:
                    self.logger.debug(' * Invalid description for {0}/{1}'.format(package, version))
        return result

    def validate(self):
        success = True
        packages = self.get_packages()
        for package in packages:
            package_description = self.parse_description(package)
            versions = self.get_versions(package)
            for version in versions:
                version_description = self.parse_description(package, version)
                path = os.path.join(os.path.join(self.path, package), version)
                for key, value in package_description.iteritems():
                    version_description.setdefault(key, value)
                if not self.validate_description(version_description):
                    print "{0}/{1}: description invalid".format(package, version)
                    success = False
                else:
                    if not os.path.isfile(os.path.join(path, version_description['license-file'])):
                        print "{0}/{1}: license file does not exist".format(package, version)
                        success = False
                    for file in version_description['files']:
                        if not os.path.isfile(os.path.join(path, file)):
                            print "{0}/{1}: referenced file does not exist: {2}".format(package, version, file)
                            success = False
        return success

class AccessLogParser:
    ACCESS_LOG_PATTERN = re.compile(r'\d+\.\d+.\d+.\d+ [^ ]+ - \[([^\]]+)\] "GET /static/res/([^/]+)/([^/]+)/[^ ]+ [^"]+" \d+ \d+ "https?://tools.wmflabs.org/([^/]+)/[^"]*" ".*')
    DATE_FORMAT = '%d/%b/%Y:%H:%M:%S +0000'

    def __init__(self, file):
        self.file = file
        self.pivot_date = datetime.datetime.now() + datetime.timedelta(days=-30)

    def parse(self):
        usage = dict()
        with open(self.file) as f:
            for line in f:
                result = self.parse_line(line)
                if result is not None:
                    (package, version, tool) = result
                    if not package in usage:
                        usage[package] = dict()
                    if not version in usage[package]:
                        usage[package][version] = dict()
                    if not tool in usage[package][version]:
                        usage[package][version][tool] = 0
                    usage[package][version][tool] += 1
        return usage

    def parse_line(self, line):
        match = AccessLogParser.ACCESS_LOG_PATTERN.match(line)
        if match:
            (date_string, package, version, tool) = match.groups()
            date = datetime.datetime.strptime(date_string, AccessLogParser.DATE_FORMAT)
            if date > self.pivot_date:
                return (package, version, tool)
        return None
