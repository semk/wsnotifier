#!/usr/bin/env python
#
# Author: Sreejith Kesavan <sreejithemk@gmail.com>
#
# Description: Gevent based Asynchronous WebSocket Server with HTTP forwarder APIs


import ConfigParser

from setuptools import setup, find_packages


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
    version='1.0.1',
    keywords='websocket http ws server',
    packages=find_packages(exclude=('unittests', 'unittests.*')),
    entry_points={
        'console_scripts': ['wsnotifier = wsnotifier.notifier:run_wsnotifier_with_default_config']
    },
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    zip_safe=True,
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
)

