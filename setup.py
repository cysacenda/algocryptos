from setuptools import setup

setup(
    name='algocryptos',
    version='0.0.1',
    packages=['dataimporter', 'algokpi', 'dataimporter/utils', 'dataimporter/config', 'dataimporter/reddit',
              'dataimporter/dbaccess', 'dataimporter/extractdata', 'dataimporter/coinmarketcap',
              'dataimporter/cryptocompare'],
    package_dir={'algokpi': 'algokpi', 'dataimporter': 'dataimporter'},
    install_requires=['requests', 'logging', 'configparser', 'ratelimit', 'psycopg2', 'tzlocal'],
    url='',
    license='',
    author='csacenda',
    author_email='',
    description=''
)
