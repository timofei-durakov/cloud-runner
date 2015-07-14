#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup (
    name = "cloud-runner",
    version = "0.1",
    description="Tool for local devstack multinode deployment",
    long_description="""\
	Tool for local devstack multinode deployment
""",
    author="Timofey Durakov",
    author_email="", # Removed to limit spam harvesting.
    url="",
    #package_dir = {'': 'src'}, # See packages below
    #packages = find_packages(exclude="test"),
    # Use this line if you've uncommented package_dir above.
    #packages = find_packages("src", exclude="tests"),
    include_package_data = True,
    zip_safe = True,
    entry_points={
        'console_scripts': [
            'cloudrunner = cloudrunner.manager.manager:main',
        ],
    },
    install_requires=[
          'jinja2',
          'netaddr'
      ]

)
