#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

with open('pip-requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n')
    ]

setup(
    name = "deploycron",
    version = "0.0.1",
    author = "monklof",
    author_email = "monklof@gmail.com",
    description = ("a small crontab deploy/install tool for python"),
    license = "MIT",
    keywords = "crontab, cron, initialize",
    url = "https://github.com/monklof/deploycron",
    packages=['deploycron', 'tests'],
    test_suite = 'nose.collector',
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points = {
        "console_scripts": [
            "deploycron_file = deploycron.cli_deploycron_file:main",
            "undeploycron_between = deploycron.cli_undeploycron_between:main"
        ]
    }
)
