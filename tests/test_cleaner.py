import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.cleaner.cleaner import MarketDataCleaner

# Sample data for testing
market_data = pd.DataFrame([
    {"Symbol": "AAPL", "InstrumentType": "Stock", "Exchange": "NASDAQ", "OpenPrice": "150.0", "HighPrice": "155.0", "LowPrice": "149.0", "ClosePrice": "154.0", "Volume": "1000000", "OpenInterest": "5000", "Date": "2024-04-01"},
    {"Symbol": "GOOG", "InstrumentType": "Stock", "Exchange": "NASDAQ", "OpenPrice": "abc", "HighPrice": "155.0", "LowPrice": "149.0", "ClosePrice": "154.0", "Volume": "1000000", "OpenInterest": "5000", "Date": "2024-04-01"},
    {"Symbol": "AAPL", "InstrumentType": "Stock", "Exchange": "NASDAQ", "OpenPrice": "150.0", "HighPrice": "155.0", "LowPrice": "149.0", "ClosePrice": "154.0", "Volume": "1000000", "OpenInterest": "5000", "Date": "invalid-date"},
    {"Symbol": "FAKE", "InstrumentType": "Stock", "Exchange": "UNKNOWN", "OpenPrice": "150.0", "HighPrice": "155.0", "LowPrice": "149.0", "ClosePrice": "154.0", "Volume": "1000000", "OpenInterest": "5000", "Date": "2024-04-01"},
])

reference_data = pd.DataFrame([
    {"Symbol": "AAPL", "InstrumentType": "Stock", "Exchange": "NASDAQ", "Status": "Active"},
    {"Symbol": "GOOG", "InstrumentType": "Stock", "Exchange": "NASDAQ", "Status": "Active"},
])

def test_cleaning_and_validation(tmp_path):
    market_path = tmp_path / "market.csv"
    reference_path = tmp_path / "reference.csv"
    market_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner(validate_active_only=True, track_dropped_rows=True)
    cleaner.load_data(str(market_path), str(reference_path))
    cleaner.clean()
    df = cleaner.get_clean_data()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1  # Only one row (AAPL) is valid and clean
    assert df.iloc[0]["Symbol"] == "AAPL"

def test_summary_does_not_fail(tmp_path):
    market_path = tmp_path / "market.csv"
    reference_path = tmp_path / "reference.csv"
    market_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner()
    cleaner.load_data(str(market_path), str(reference_path))
    cleaner.clean()

    # Should log summary, not raise
    cleaner.summary()

    df = cleaner.get_clean_data()
    assert not df.empty

def test_duplicate_and_empty_rows(tmp_path):
    duplicated_data = market_data.copy()
    duplicated_data = pd.concat([duplicated_data, duplicated_data.iloc[[0]]], ignore_index=True)  # Add duplicate
    duplicated_data.loc[4] = [None] * len(duplicated_data.columns)  # Add empty row

    market_path = tmp_path / "market_dup.csv"
    reference_path = tmp_path / "reference.csv"
    duplicated_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner()
    cleaner.load_data(str(market_path), str(reference_path))
    cleaner.clean()
    df = cleaner.get_clean_data()

    # Still only one valid row after duplicates and empty removed
    assert len(df) == 1

def test_whitespace_trimming(tmp_path):
    dirty_data = market_data.copy()
    dirty_data.loc[0, "Symbol"] = " AAPL  "

    market_path = tmp_path / "market_trim.csv"
    reference_path = tmp_path / "reference.csv"
    dirty_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner()
    cleaner.load_data(str(market_path), str(reference_path))
    cleaner.clean()
    df = cleaner.get_clean_data()

    assert len(df) == 1
    assert df.iloc[0]["Symbol"] == "AAPL"

def test_clean_fails_without_load():
    cleaner = MarketDataCleaner()
    with pytest.raises(ValueError, match="Data not loaded"):
        cleaner.clean()

def test_get_data_fails_without_clean():
    cleaner = MarketDataCleaner()
    cleaner.market_df = pd.DataFrame()
    cleaner.instrument_df = pd.DataFrame()
    with pytest.raises(ValueError, match="Data has not been cleaned"):
        cleaner.get_clean_data()

def test_missing_required_columns(tmp_path):
    broken_data = pd.DataFrame([
        {"Symbol": "AAPL", "Exchange": "NASDAQ", "OpenPrice": "150.0", "Date": "2024-04-01"}  # Missing InstrumentType & other price fields
    ])

    market_path = tmp_path / "market_broken.csv"
    reference_path = tmp_path / "reference.csv"
    broken_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner()
    cleaner.load_data(str(market_path), str(reference_path))
    with pytest.raises(KeyError):
        cleaner.clean()

def test_dot_in_symbol_fix(tmp_path):
    market_data = pd.DataFrame([
        {"Symbol": "AAPL.NYSE", "InstrumentType": "Stock", "Exchange": "", "OpenPrice": 150, "HighPrice": 155, "LowPrice": 149, "ClosePrice": 154, "Volume": 1000000, "OpenInterest": 5000, "Date": "2024-04-01"},
    ])
    reference_data = pd.DataFrame([
        {"Symbol": "AAPL", "InstrumentType": "Stock", "Exchange": "NYSE", "Status": "Active"},
    ])
    market_path = tmp_path / "market.csv"
    reference_path = tmp_path / "reference.csv"
    market_data.to_csv(market_path, index=False)
    reference_data.to_csv(reference_path, index=False)

    cleaner = MarketDataCleaner(fix_dot_in_symbol=True)
    cleaner.load_data(str(market_path), str(reference_path))
    cleaner.clean()
    df = cleaner.get_clean_data()

    assert len(df) == 1
    assert df.iloc[0]['Symbol'] == 'AAPL'
    assert df.iloc[0]['Exchange'] == 'NYSE'

