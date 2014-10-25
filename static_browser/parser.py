# coding=utf-8

import json
import logging
import os
import os.path

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
