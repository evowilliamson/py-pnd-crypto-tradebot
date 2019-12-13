#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md") as f:
    long_desc = f.read()

setup(name="py-pnd-crypto-tradebot",
      version=0.1,
      description="A crypto pump and dump detecting tradebot in Python",
      long_description=long_desc,
      long_description_content_type="text/markdown", 
      keywords = "crypto tradebot algorithm pump dump python",
      author="Evo Williamson",
      author_email="evowilliamson@gmail.com",
      license="GNU General Public License, version 2",
      url="https://github.com/evowilliamson/py-pnd-crypto-tradebot",
      packages=find_packages(),
      install_requires=[],
      test_suite="tests",
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent"
        ,
      ]
     )
