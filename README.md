# pygameday
Pygameday scrapes Major League Baseball's [GameDay](http://mlb.mlb.com/mlb/gameday/#) 
data, parses it, and inserts it into a database of your choosing for 
later analysis.

Games, Players, At-Bats, Hits In Play, and Pitches are the data types
captured.

One of the motivations behind creating pygameday was to make the 
database backend transparent; you should not have to worry about
whether you're using SQLite, Postgres, or some other implementation.
All you do is specify a URI to the database, and you're up and 
running.

Pygameday is build on [SQLAlchemy](http://www.sqlalchemy.org/), and 
should therefore be compatible with any database that SQLAlchemy 
supports. As of this writing, the following dialects are supported:

* SQLite
* PostgreSQL
* MySQL
* Oracle
* Microsoft SQL Server
* Firebird
* Sybase

It should be noted that I've tested only SQLite and Postgres.

## Installation
Install pygameday using `pip`:

```python
pip install pygameday
```

Pygameday was developed and tested using Python 2.7. It may run 
with Python 3, but I need to do more testing.

## Quickstart
Pygameday can be run in two modes:  by instantiating a GameDayClient 
in your own Python code, or by using the command line tool.

### Using the GameDayClient
First, instantiate the database client. All you need to do is 
specify the database URI. This example creates an SQLite database
named `gameday.db` in the current directory, but you can substitute
a URI for your database flavor of choice.

```python
from pygameday import GameDayClient
database_uri = "sqlite:///gameday.db"
client = GameDayClient(database_uri)
```

Ingest games that occurred on a single day by specifying a date.
```python
client.process_date("2015-05-01")  # Ingest games on May 1, 2015
```

You can also ingest games within a date range.
```python
# Ingest games between May 1, 2015 and May 3, 2015
client.process_date_range("2015-05-01", "2015-05-03")
```

After ingesting data, use any tool you like to verify that the 
data is in the database. Here's an example using [pandas](http://pandas.pydata.org/).

```python
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine(database_uri)

# Execute SQL queries against the database we just created
data = pd.read_sql_query("SELECT * FROM games LIMIT 5", engine)
data.head()
```

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

Pygameday will ingest GameDay data for games played on the 
specified day, including information for games, atbats, hits in play, 
pitches, and players. 

Alternatively, you can specify two dates on the command line, and
pygameday will retrieve and ingest data for games on all days 
in the date range represented by the given dates.  For example:

```
$ python main.py 2015-05-31 2015-06-02
```

## Database Configuration
You only need to specify the URI for the database for pygameday to work.
Here are some example URIs.

**SQLite**: 
* `"sqlite:///example.db"  # File in the current directory`
* `"sqlite:////absolute/path/to/example.db"  # Absolute path to file (Unix/Mac)`
* `"sqlite:///C:\absolute\path\to\example.db"  # Absolute path to file (Windows)`

**PostgreSQL**:
* `"postgresql://user:password@host/database_name"  # Standard Postgres dialect`
* `"psycopg2+postgresql://user:password@host/database_name"  # with psycopg2 driver`

SQLAlchemy's [engine documentation](http://docs.sqlalchemy.org/en/latest/core/engines.html)
has additional details about the dialects it supports.

## TODO
* Better, more comprehensive unit testing
* Ensure Python 3 compatibility
* Enable multi-threaded processing
