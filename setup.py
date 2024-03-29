# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='twitter-bots',
    version='0.1.0',
    description='Twitter bots that listen to twitter and reacts',
    long_description=readme,
    author='Edmond Lafay-David',
    author_email='seigneurcanard@gmail.com',
    url='https://github.com/edmondlafay/twitter-bots',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

