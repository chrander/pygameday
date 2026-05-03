# pygameday
Pygameday fetches MLB [Statcast](https://baseballsavant.mlb.com/) pitch-by-pitch data
and ingests it into a relational database of your choosing for later analysis.

Data captured per game: Games, Players, At-Bats, Pitches, and Hits In Play — including
full Statcast physics (release speed, spin rate, break, launch angle, exit velocity, etc.).

Data is sourced from [Baseball Savant](https://baseballsavant.mlb.com/) via
[pybaseball](https://github.com/jldbc/pybaseball). Coverage begins with the 2015 season
(when Statcast was fully deployed across all stadiums).

Pygameday is built on [SQLAlchemy](http://www.sqlalchemy.org/) and is compatible with any
database it supports:

* SQLite
* PostgreSQL
* MySQL
* Oracle
* Microsoft SQL Server

SQLite and PostgreSQL have been tested.

## Examples
The [examples](./examples) directory contains a documented
[Jupyter notebook](./examples/example.ipynb) and a stripped-down
[script](./examples/example.py).

## Installation

```
pip install pygameday
```

Requires Python 3.11+. Dependencies (`pybaseball`, `sqlalchemy`, `pandas`, `tqdm`) are
installed automatically.

## Quickstart

### Using the StatcastClient

Instantiate the client with a database URI. The database and tables are created
automatically if they don't exist.

```python
from pygameday import StatcastClient

database_uri = "sqlite:///gameday.db"
client = StatcastClient(database_uri)
```

Ingest all games on a single day:

```python
from datetime import datetime

client.process_date(datetime(2023, 7, 4))
```

Ingest a date range (inclusive):

```python
start_date = datetime(2023, 4, 1)
end_date   = datetime(2023, 4, 7)
client.process_date_range(start_date, end_date)
```

By default spring training and exhibition games are skipped. To include them:

```python
client = StatcastClient(database_uri, ingest_spring_training=True)
```

### Querying the data

After ingesting, query with any tool that speaks SQL. Example using pandas:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(database_uri)
pitches = pd.read_sql("SELECT * FROM pitches LIMIT 10", engine)
pitches.head()
```

Key tables:

| Table | Description |
|---|---|
| `games` | One row per game (`game_pk`, teams, score, date) |
| `at_bats` | One row per plate appearance (`events`, balls/strikes/outs) |
| `pitches` | One row per pitch (velocity, location, movement, spin) |
| `hits_in_play` | Balls put in play (`launch_speed`, `launch_angle`, `hc_x/y`) |
| `players` | Unique batters and pitchers (MLBAM ID, name, bats/throws) |

## Database Configuration

Pass any valid SQLAlchemy connection URI to `StatcastClient`.

**SQLite**:
* `"sqlite:///example.db"` — file in the current directory
* `"sqlite:////absolute/path/to/example.db"` — absolute path (Unix/Mac)

**PostgreSQL**:
* `"postgresql://user:password@host/database_name"`
* `"postgresql+psycopg2://user:password@host/database_name"` — with psycopg2 driver

See SQLAlchemy's [engine documentation](https://docs.sqlalchemy.org/en/20/core/engines.html)
for all supported dialects.
