#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:
    import py2exe
except:
    pass

from app_automatico import telas

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    windows=[{'script':'app_automatico/telas/appautomaticodlg.py'}, ],
    # data_files = ['app_automatico/telas/testes/ui_findandreplacedlg.py'],
    options={"py2exe":{
                # 'packages':['app_automatico'],

                'bundle_files': 1,
                'compressed': True,
                "includes":["sip","PyQt4.QtGui", "app_automatico"],
                "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"]
                        }},

    name='app_automatico',
    version='0.1.0',
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    long_description=readme + '\n\n' + history,
    author="Dyeden Monteiro",
    author_email='dyedenm@gmail.com',
    url='https://github.com/dyeden/app_automatico',
    packages = find_packages(),
    package_dir={'app_automatico':
                 'app_automatico'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    zipfile = None,
    keywords='app_automatico',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
