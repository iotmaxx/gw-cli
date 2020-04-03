# -*- coding:utf-8 -*-
# @Script: setup.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-23 23:04:16
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-04-03 12:59:25
# @Description: Setupfile to install gw-cli.

from setuptools import setup

setup(
    name='gw-cli',
    version='0.1',
    description='Gw-CLI to change network settings on Linux based systems',
    author='Andre Litty',
    author_email='alittysw@gmail.com',
    url='https://github.com/iotmaxx/gw-cli',
    py_modules=['gw_cli'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        gw_cli=gw_cli:cli
    '''
)
