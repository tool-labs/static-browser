# coding=utf-8

import datetime
import json
import logging
import os
import os.path
import re
import sets

class NewPackageParser:
    DESCRIPTION_FILE = 'index.json'
    KEY_TITLE = 'title'
    KEY_LICENSE = 'license'
    KEY_LICENSE_FILE = 'license-file'
    KEY_FILES = 'files'
    KEY_DESCRIPTION = 'description'
    KEY_HOMEPAGE = 'homepage'
    KEY_FONTS = 'fonts'
    KEY_FONTS_EOT = 'eot'
    KEY_FONTS_SVG = 'svg'
    KEY_FONTS_TTF = 'ttf'
    KEY_FONTS_WOFF = 'woff'
    REQUIRED_KEYS_PACKAGE = [KEY_TITLE]
    REQUIRED_KEYS_PACKAGE_VERSION = [KEY_LICENSE, KEY_LICENSE_FILE]
    KEYS_FONT_TYPE = [KEY_FONTS_EOT, KEY_FONTS_SVG, KEY_FONTS_TTF, KEY_FONTS_WOFF]

    def __init__(self, path):
        self._path = path
        self._parsed = False
        self._logger = logging.getLogger(__name__)

    def get_library_package_versions(self):
        if not self._parsed:
            self._parse()
        return self._get_package_versions_from_list(self._data_libraries)

    def get_font_package_versions(self):
        if not self._parsed:
            self._parse()
        return self._get_package_versions_from_list(self._data_fonts)

    def get_package_version(self, package, version):
        if self._parsed:
            if not package in self._data or not version in self._data[package]:
                return None
            return self._data[package][version]
        self._logger.info('Loading {0} {1}'.format(package, version))
        return self._load_package_version(package, version)

    def get_package_description(self, package):
        if not self._validate_package(package):
            return None
        package_description = self._load_description(package)
        if not self._validate_package_description(package_description):
            return None
        return package_description

    def get_package_versions(self, package):
        if self._parsed:
            if not package in self._data:
                return None
            return self._data[package]

        self._logger.info('Loading {0} versions'.format(package))
        if not self._validate_package(package):
            return None
        package_description = self._load_description(package)
        if not self._validate_package_description(package_description):
            return None
        versions = dict()
        version_list = self._find_package_versions(package=package)
        for version in version_list:
            self._logger.info('Loading {0} {1}'.format(package, version))
            version_data = self._load_package_version(package, version, package_valid=True, package_description=package_description)
            if version_data:
                versions[version] = version_data
        return versions

    def validate(self):
        valid = True
        all_package_versions = self._find_package_versions()
        for package in all_package_versions:
            package_description = self._load_description(package)
            if not self._validate_package_description(package_description):
                self._logger.error('Invalid package description for {0}'.format(package))
                valid = False
            for version in all_package_versions[package]:
                package_version_description = self._load_description(package, version)
                if not self._validate_package_version_description(package, version, package_version_description):
                    self._logger.error('Invalid package version description for {0} {1}'.format(package, version))
                    valid = False
        return valid

    def get_all_files(self, package, version):
        return self._get_all_files_in_dir(os.path.join(self._path, package, version))

    def _get_all_files_in_dir(self, directory, basepath=''):
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                if not basepath + item == 'index.json':
                    files.append(basepath + item)
            elif os.path.isdir(item_path):
                for file in self._get_all_files_in_dir(item_path, item + '/'):
                    files.append(file)
        return files

    def _get_package_versions_from_list(self, package_versions):
        data = dict()
        for (package, version) in package_versions:
            package_version_data = self.get_package_version(package, version)
            if package_version_data:
                if not package in data:
                    data[package] = dict()
                data[package][version] = package_version_data
        return data

    def _validate_package(self, package):
        package_path = os.path.join(self._path, package)
        package_description = os.path.join(package_path, self.DESCRIPTION_FILE)
        valid = False
        if not os.path.isdir(package_path):
            self._logger.warning('Package at {0} does not exist'.format(package_path))
        elif not os.path.isfile(package_description):
            self._logger.warning('Package description at {0} does not exist'.format(package_description))
        else:
            valid = True
        return valid

    def _validate_package_version(self, package, version, package_valid=False):
        if not package_valid and not self._validate_package(package):
            self._logger.warning('Package invalid')
            return False
        version_path = os.path.join(self._path, package, version)
        version_description = os.path.join(version_path, self.DESCRIPTION_FILE)
        valid = False
        if not os.path.isdir(version_path):
            self._logger.warning('Package version at {0} does not exist'.format(version_path))
        elif not os.path.isfile(version_description):
            self._logger.warning('Package version description at {0} does not exist'.format(version_description))
        else:
            valid = True
        return valid

    def _find_package_versions(self, package=None):
        if package:
            self._logger.debug('Looking for package versions of {0}'.format(package))
            versions = []
            package_path = os.path.join(self._path, package)
            for version in os.listdir(package_path):
                if version != self.DESCRIPTION_FILE:
                    self._logger.debug('Checking version {0}'.format(version))
                    if self._validate_package_version(package, version, package_valid=True):
                        self._logger.debug('Version is valid')
                        versions.append(version)
                    else:
                        self._logger.warning('Version is invalid')
            return versions
        else:
            packages = {}
            self._logger.debug('Looking for packages')
            for package in os.listdir(self._path):
                self._logger.debug('Checking package ' + package)
                if self._validate_package(package):
                    self._logger.debug('Looking for package versions')
                    versions = self._find_package_versions(package)
                    if versions:
                        self._logger.debug('Found {0} version(s)'.format(len(versions)))
                        packages[package] = versions
                    else:
                        self._logger.warning('No versions found')
                else:
                    self._logger.warning('Package is invalid')
            return packages

    def _load_description(self, package, version=None):
        path = os.path.join(self._path, package)
        if version:
            path = os.path.join(path, version)
        path = os.path.join(path, self.DESCRIPTION_FILE)
        with open(path) as f:
            try:
                result = json.load(f)
                result['name'] = package
                if version:
                    result['version'] = version
                return result
            except:
                return dict()

    def _validate_description(self, description, required, optional=[]):
        valid = True
        if optional:
            valid = False
            for item in optional:
                if item in description:
                    valid = True
            if valid:
                self._logger.debug('At least one optional found')
            else:
                self._logger.warning('No optional present')
        for item in required:
            if item in description:
                self._logger.debug('Required item {0} found'.format(item))
            else:
                self._logger.warning('Required item {0} missing'.format(item))
                valid = False
        return valid

    def _validate_file(self, package, version, file):
        file_path = os.path.join(self._path, package, version, file)
        if os.path.isfile(file_path):
            self._logger.debug('Required file {0} exists'.format(file_path))
            return True
        else:
            self._logger.warning('Required file {0} does not exist'.format(file_path))
            return False

    def _validate_package_description(self, description):
        return self._validate_description(description, self.REQUIRED_KEYS_PACKAGE)

    def _validate_package_version_description(self, package, version, description):
        self._logger.debug('Validating description for {0} {1}'.format(package, version))
        valid = self._validate_description(description, self.REQUIRED_KEYS_PACKAGE_VERSION, [self.KEY_FILES, self.KEY_FONTS])
        if valid:
            if self.KEY_FILES in description:
                for file in description[self.KEY_FILES]:
                    valid = valid and self._validate_file(package, version, file)
            if self.KEY_FONTS in description:
                for key in description[self.KEY_FONTS]:
                    valid = self._validate_description(description[self.KEY_FONTS][key], [],
                            self.KEYS_FONT_TYPE)
                    for (item, value) in description[self.KEY_FONTS][key].iteritems():
                        valid = valid and self._validate_file(package, version, value)
        return valid

    def _combine_description(self, data, defaults):
        result = dict(defaults)
        for key in data:
            result[key] = data[key]
        return result

    def _load_package_version(self, package, version, package_valid=False, package_description=None):
        if not self._validate_package_version(package, version, package_valid=package_valid):
            return None
        if not package_description:
            package_description = self._load_description(package)
            if not package_valid and not self._validate_package_description(package_description):
                return None
        description = self._load_description(package, version)
        if not self._validate_package_version_description(package, version, description):
            return None
        description = self._combine_description(description, package_description)
        return description

    def _parse(self):
        all_package_versions = self._find_package_versions()
        data = dict()
        data_fonts = []
        data_libraries = []
        for package in all_package_versions:
            versions = self.get_package_versions(package)
            if versions:
                data[package] = versions
                for version in versions:
                    if self.KEY_FONTS in versions[version]:
                        data_fonts.append((package, version))
                    if self.KEY_FILES in versions[version]:
                        data_libraries.append((package, version))
        self._data = data
        self._data_fonts = data_fonts
        self._data_libraries = data_libraries
        self._parsed = True


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
            if not tool == 'static' and date > self.pivot_date:
                return (package, version, tool)
        return None
