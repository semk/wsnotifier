#!/usr/bin/env python
#
# Author: Sreejith Kesavan <sreejithemk@gmail.com>
#
# Description: Gevent based Asynchronous WebSocket Server with HTTP APIs.


import ConfigParser

from setuptools import setup, find_packages


def prepare_version():
    """
    Method to prepare release version, _build_number will be used for internal purpose
    :return:
    """
    config = ConfigParser.ConfigParser()
    config.read('version.txt')
    section = 'version'
    _major_release = config.getint(section, 'major.release')
    _minor_release = config.getint(section, 'minor.release')
    _point_release = config.getint(section, 'point.release')
    _build_number = config.getint(section, 'build.number')
    if _build_number != 0:
        return "%s.%s.%s.%s" % (_major_release, _minor_release, _point_release, _build_number)
    else:
        return "%s.%s.%s" % (_major_release, _minor_release, _point_release)


tests_require = ['nose == 1.3.7', 'mock == 1.3.0', 'coverage >= 4.0.3']

install_requires = [
    'gevent == 1.1.1',
    'gunicorn == 19.4.5',
    'Flask-Sockets == 0.2.0',
    'flask == 0.10.1',
    'requests == 2.9.1',
    'python-dateutil == 2.5.3'
]


setup(
    author='Sreejith Kesavan',
    name='wsnotifier',
    description='Gevent based Asynchronous WebSocket Server with HTTP APIs.',
    version=prepare_version(),
    keywords='websocket http ws server',
    packages=find_packages(exclude=('unittests', 'unittests.*')),
    entry_points={
        'console_scripts': ['wsnotifier = wsnotifier.notifications:run_wsnotifier_with_default_config']
    },
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    zip_safe=False,
    platforms=['any'],
    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
)

