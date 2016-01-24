# pygameday
Tools for scraping, parsing, and ingesting Major League Baseball's 
GameDay data into a database

## Installation
Pygameday was developed and tested using Python 2.7. It may run 
with Python 3, but this has yet to be confirmed.

The full dependency list is given in `requirements.txt`.
The dependencies include:
* sqlalchemy
* psycopg2
* sqlite
* requests
* lxml
* dateutil

If you plan on using pygameday with a MySQL or Oracle database, 
you will perhaps need to install additional modules. 

## Quickstart
Pygameday can be run in two modes: from the command line, or by 
instantiating a GameDayClient in your own Python code.

### Running from the command line
To run from the command line, `cd` to the top level pygameday 
directory. This directory contains files called `config.py` and 
`main.py`. To run the GameDay client, execute 
`python main.py [yyyy-mm-dd]`, 
where `yyyy` is a four-digit year, `mm` is a two-digit month, and 
`dd` is a two-digit day.  For example:

```
$ python main.py 2015-05-30
```

Pygameday will download GameDay data for games played on the 
specified day, including information for games, atbats, hits in play, 
pitches, and players. After running this command, you should notice
that you have 

Alternatively, you can specify two dates on the command line, and
pygameday will retrieve and ingest data for games on all days 
in the date range represented by the given dates.  For example:

```
$ python main.py 2015-05-31 2015-06-02
```

### Instantiating a GameDayClient

## Configuring the Database
