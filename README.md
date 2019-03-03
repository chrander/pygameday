# pygameday
Pygameday scrapes Major League Baseball (MLB) [GameDay](http://mlb.mlb.com/mlb/gameday/#) 
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

```
pip install pygameday
```

Pygameday depends on tqdm, sqlalchemy, lxml, requests, and python-dateutil. If
those packages are not automatically installed, run

```
pip install tqdm sqlalchemy lxml requests python-dateutil
```

Pygameday was developed and tested using Python 3.

## Quickstart
Run pygameday by instantiating a GameDayClient.

### Using the GameDayClient
First, instantiate the database client by specifying a database URI. 
This example creates an SQLite database
named `gameday.db` in the current directory, but you can substitute
a URI for your database flavor of choice, as long as the database is supported
by SQLAlchemy.

The `n_workers` parameter determines how many parallel processes are
used to insert game data. By default, `n_workers` is set to 4. To handle database 
inserts serially, set `n_workers=1`. Serial processing tends to work better for SQLite
databases, which is why it's used in this example, but a server-based 
database implementation should be able to handle parallel processes.

```python
from pygameday import GameDayClient
database_uri = "sqlite:///gameday.db"
client = GameDayClient(database_uri, n_workers=1)
```

Ingest games that occurred on a single day by specifying a standard Python datetime.
```python
from datetime import datetime

date_to_process = datetime(2015, 5, 1)  # Ingest games on May 1, 2015
client.process_date(date_to_process)
```

You can also ingest games within a date range.
```python
# Ingest games between May 1, 2015 and May 3, 2015
start_date = datetime(2015, 5, 1)
end_date = datetime(2015, 5, 3)
client.process_date_range(start_date, end_date)
```

After ingesting data, use any tool you like to verify that the 
data is in the database. Here's an example using [pandas](http://pandas.pydata.org/).

```python
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine(database_uri)

# Execute SQL queries against the database we just created
data = pd.read_sql("SELECT * FROM games LIMIT 5", engine)
data.head()
```

## Database Configuration
You  need to specify a valid database URI for pygameday to work.
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
