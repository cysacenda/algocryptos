from setuptools import setup

#packages=['', 'dataimporter/utils', 'dataimporter/config', 'dataimporter/reddit', 'dataimporter/dbaccess', 'dataimporter/extractdata', 'dataimporter/coinmarketcap', 'dataimporter/cryptocompare'],


setup(
    name='algocryptos',
    version='0.0.1',
packages=['', 'dataimporter','algokpi'],
    package_dir={'algokpi': 'algokpi', 'dataimporter': 'dataimporter'},
    install_requires=['requests', 'logging', 'configparser', 'ratelimit', 'psycopg2', 'tzlocal'],
    url='',
    license='',
    author='csacenda',
    author_email='',
    description=''
)
