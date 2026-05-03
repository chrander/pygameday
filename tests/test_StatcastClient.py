from datetime import datetime

from pygameday import StatcastClient


def test_ingest():
    client = StatcastClient('sqlite:///gameday.db')
    client.db_stats()
    client.process_date_range(datetime(2023, 7, 4), datetime(2023, 7, 4))
    client.db_stats()
