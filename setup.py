# from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'pygameday',
    version = '0.3.4',
    author = 'Chris Anderson',
    author_email = 'christian.c.anderson@gmail.com',
    packages = setuptools.find_packages(),
    url = 'https://github.com/chrander/pygameday',
    license='LICENSE.txt',
    description = 'Module for scraping, parsing, and ingesting MLB GameDay data into a database',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'tqdm',
        'sqlalchemy',
        'python-dateutil',
        'requests',
        'lxml'
    ],
    download_url = 'https://github.com/chrander/pygameday/tarball/0.3.4',
    keywords = ['baseball', 'gameday', 'database', 'scraping'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
