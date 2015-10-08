#!/usr/bin/env python
from setuptools import setup

setup(
    name="cloud-runner",
    version="0.1",
    description="Tool for local devstack multinode deployment",
    author="Timofey Durakov",
    author_email="",
    url="",
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'cloudrunner = cloudrunner.cmd:main',
        ],
    },
    install_requires=[
        'jinja2',
        'netaddr',
        'pycrypto'

    ]
)
