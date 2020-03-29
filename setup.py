# -*- coding:utf-8 -*-
# @Script: setup.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-23 23:04:16
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-03-29 13:49:33
# @Description: Setupfile to install gw-cli.

from setuptools import setup

setup(
    name='gw-cli',
    version='0.1',
    py_modules=['gw_cli'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        gw_cli=gw_cli:cli
    '''
)
