from datetime import datetime

from pygameday import scrape


def test_fetch_statcast_data():
    """Verify that a known regular-season date returns pitch data."""
    date = datetime(2023, 7, 4)
    df = scrape.fetch_statcast_data(date, date)
    assert df is not None
    assert not df.empty
    assert 'game_pk' in df.columns
    assert 'pitch_type' in df.columns
    assert 'release_speed' in df.columns
    assert 'plate_x' in df.columns
