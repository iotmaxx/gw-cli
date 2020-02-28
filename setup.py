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
        yourscript=yourscript:cli
    '''
)
