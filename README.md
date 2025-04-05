# Market Data Cleaning & Wrapping Solution

## 🧾 Overview

This project provides a Python-based solution to clean and validate market data received from a vendor.

The data pipeline is structured to first clean the raw data (e.g., converting prices, parsing dates, dropping malformed rows),
and only then validate the cleaned entries against the instrument reference data. This ensures a clear separation between
data quality issues and business rule violations.

Throughout the process, a structured logger is used to:
- Track progress at each stage
- Report dropped rows with specific reasons (e.g., missing price, invalid date, invalid reference)
- Summarize the cleaned dataset The core functionality is wrapped in a `MarketDataCleaner` class, which:

- Loads raw market data and instrument reference files
- Cleans up data inconsistencies, formatting issues, and missing values
- Validates instrument information against reference data
- Exposes a clean, queryable DataFrame or further extension hooks

---

## 📌 Assumptions

- **Instrument validation** is based on matching `Symbol`, `InstrumentType`, and `Exchange` against the reference file.
- Only **active instruments** (with `Status == "Active"`) are considered valid.
- Critical price fields (`OpenPrice`, `ClosePrice`, `HighPrice`, `LowPrice`) must be present and numeric. Rows missing any of these will be dropped.
- `Volume` and `OpenInterest` are optional but cleaned where present.
- Dates in `financial_market_data.csv` are assumed to be in `YYYY-MM-DD` format and are parsed into datetime. If a date is invalid or cannot be parsed, the entire row will be dropped during cleaning.
- The reference data may contain extra fields (e.g., `Sector`, `ContractMonth`) that are used for optional enrichment but not mandatory.

---

## 🧠 Technology Choices

### Why Object-Oriented Design?
The trader requested a wrapper class to manage and expose basic functionality around data loading and validation. Using an object-oriented (OOP) approach allows us to encapsulate the data, configuration, and methods for cleaning, validation, and summarization within a single class (`MarketDataCleaner`). This results in:
- Clean separation of concerns
- Easy reuse and extension (e.g., swapping data sources, adding exports)
- Convenient state tracking for multiple processing stages
- Enhanced testability and modular structure

### Functional Enhancements (Future Option)
For more advanced pipelines, the logic can be refactored to support functional composition or pipeline processing, for example:
- Breaking out transformation steps into pure functions
- Allowing partial pipelines for streaming or distributed computing (e.g., with Dask or PySpark)
- Using `@dataclass` for immutable config settings or results

For this scope and file size, OOP was the most practical and trader-aligned approach.



### Why Pandas?

Pandas was chosen for this solution as it offers a highly expressive and readable API for working with tabular data. It is widely adopted in both data science and engineering contexts, and is perfectly suited for cleaning, transforming, and validating CSV-based market data.

Although some alternatives like Polars, Dask, or DuckDB offer more efficient handling of large-scale or streaming data, **the dataset provided (~1 million rows)** is comfortably within the performance range of Pandas on a modern laptop. Pandas also benefits from strong ecosystem support (e.g., NumPy, date parsing, regex, and exporting capabilities), making it an ideal fit for a well-rounded and maintainable solution.

Had the dataset been significantly larger (e.g., 10M+ rows or multi-GB scale), a more scalable solution using Polars or chunked I/O with Dask might be more appropriate.

In summary:
- ✅ Fast enough for the dataset size
- ✅ Clean and concise API
- ✅ Familiar to most Python developers
- ✅ Rich feature set for cleaning and transformation

---

## 🚀 How to Run

1. Make sure you have Python 3.12+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the solution:
   ```bash
   python main.txt
   ```

This will:
- Load both CSV files
- Clean and validate the market data
- Print a brief summary
- Optionally export the cleaned data (if implemented)

---

## 🧪 Testing

Basic validation is provided in `tests/test_cleaner.py` using `pytest`. To run tests:

```bash
pytest -v
```

---

## 📁 Files Included

- `main.txt`: Entry point to run the solution (renamed from `.py` for email compatibility)
- `cleaner/cleaner.py`: Main class implementation
- `tests/test_cleaner.py`: Pytest-based tests
- `requirements.txt`: Dependencies
- `README.md`: Project documentation
- `data/*.csv`: Raw input files

---

## 🧩 Edge Case Handling Improvements

The cleaner now also handles:
- Trimming whitespace in key string fields (`Symbol`, `InstrumentType`, `Exchange`)
- Dropping completely empty rows
- Removing duplicate entries

## 💡 Ideas for Future Enhancements

- Add support for streaming large datasets (via chunks or generators)
- Add command-line flags or a simple CLI interface
- Export cleaned data as Parquet or upload to a database
- Enrich with sector/currency and add aggregation features
- Handle timezone-aware datetime conversion
- Improve logging and row-level error tracking

---

## 📬 Contact

Submitted by **Alex Eygenson**


## ✅ Test Coverage

Unit tests are provided in `tests/test_cleaner.py` and cover the following:

- ✔️ Valid row is retained after full cleaning and validation
- ✔️ Invalid prices, volumes, or dates are dropped
- ✔️ Only active instruments are retained (if configured)
- ✔️ Summary logs produce output without error
- ✔️ Duplicate and empty rows are removed
- ✔️ Whitespace in key string fields is trimmed
- ✔️ Raises appropriate errors if `load_data()` or `clean()` are skipped
- ✔️ Raises errors on missing required columns in input data

To run tests:
```bash
pytest -v
```

## ✅ Conclusion

This project provides a robust, maintainable solution for validating and cleaning vendor-supplied market data. It emphasizes:

- Clean separation of responsibilities using OOP
- Transparent data rejection with logging
- Safe handling of edge cases including invalid prices, dates, duplicates, and whitespace
- Configurable behavior (e.g., validation scope, logging detail)
- Thorough test coverage of core and edge logic

The solution is scalable, easy to extend, and aligns with real-world standards for financial data ingestion workflows.