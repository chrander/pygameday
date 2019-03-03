from distutils.core import setup

setup(
    name = 'pygameday',
    version = '0.3',
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
        'tqdm'
    ],
    download_url = 'https://github.com/chrander/pygameday/tarball/0.3',
    keywords = ['baseball', 'gameday', 'database', 'scraping'],
    classifiers = [],
)
