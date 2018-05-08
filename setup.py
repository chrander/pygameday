from distutils.core import setup

setup(
    name = 'pygameday',
    version = '0.2',
    author = 'Chris Anderson',
    author_email = 'christian.c.anderson@gmail.com',
    packages = ['pygameday'],
    url = 'https://github.com/chrander/pygameday',
    license='LICENSE.txt',
    description = 'Module for scraping, parsing, and ingesting MLB GameDay data into a database',
    long_description=open('README.md').read(),
    install_requires=[
        'python-dateutil',
        'sqlalchemy',

    ],
    download_url = 'https://github.com/chrander/pygameday/tarball/0.1',
    keywords = ['baseball', 'gameday', 'database', 'scraping'],
    classifiers = [],
)
