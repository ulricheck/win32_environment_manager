#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name = "environment_manager",
      version = '0.1',
      description = "Environment Manager for Win32",
      author = "Ulrich Eck",
      author_email = "ulrich.eck@tum.de",
      url = "http://campar.in.tum.de",
      packages = find_packages('.'),
      package_data = {'environment_manager' : [ 'views/*.enaml',
                                                'images/*',
                                                ]},
      #package_dir = {'git':'git'},
      license = "BSD License",
      requires=(
        'atom',
        'enaml',
        'mock',
      ),
      zip_safe=False,
      long_description = """\
This module manages Win32 Environment Variables""",
      classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        entry_points={
            'console_scripts': [
                'envmgr = environment_manager.main:main',
                ],
         },
      )
