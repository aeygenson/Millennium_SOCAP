# 🧹 Market Data Cleaning & Validation

## 📘 Overview

This project delivers a Python-based solution for ingesting, cleaning, and validating market data from a vendor.  
It was implemented with an emphasis on:

- Transparency of logic and design decisions
- Traceable, testable data cleaning
- Practical performance and extensibility

A core class `MarketDataCleaner` wraps all functionality, keeping the solution modular, readable, and adaptable.

---

## 📌 Assumptions & Design Philosophy

Clear, reasoned assumptions underpin this solution:

- ✅ **Only active instruments** from the reference file (`Status == "Active"`) are valid.
- ✅ **Price fields** (`OpenPrice`, `ClosePrice`, `HighPrice`, `LowPrice`) are required and must be numeric.
- ✅ **Volume** and **OpenInterest** are optional but cleaned if present.
- ✅ **Dates** are in `YYYY-MM-DD` format and parsed to `datetime`; invalid dates cause the row to be dropped.
- ✅ Instrument validation relies on exact matches of `Symbol`, `InstrumentType`, and `Exchange`.
- ✅ Extra fields in the reference file (e.g., `Sector`, `ContractMonth`) are ignored unless explicitly used.
- ✅ Symbols formatted like `AAPL.NYSE` will be split into `Symbol=AAPL`, `Exchange=NYSE` when `fix_dot_in_symbol=True` is enabled.


This ensures both **data quality** and **alignment with business rules** without overcomplicating the pipeline.

---

## 🧠 Technology Choices

### Why Object-Oriented Design?

Requested by the trader and purpose-built for clarity:

- Keeps logic encapsulated in a `MarketDataCleaner` class
- Enables easy reuse and future extension
- Supports parameterized configuration (e.g., validation flags)
- Encourages structured testing and debugging

### Why Pandas?

- ✅ Fast enough for datasets under ~10M rows
- ✅ Rich, expressive API for data manipulation
- ✅ Familiar to analysts and engineers alike
- ✅ Ecosystem integration (NumPy, datetime parsing, etc.)

While scalable options like Polars or Dask were considered, **Pandas was ideal** for the given file size (~1M rows) and requirements.

---

## 🛠️ How the Cleaner Works

1. **Load data** from two CSVs: market and reference
2. **Clean market data**:
   - Strip whitespace from ID fields
   - Convert prices, volume, and open interest to numeric
   - Parse and validate dates
   - Drop rows with missing price/date values
   - Remove duplicates and empty rows
3. **Validate against reference data**:
   - Filter for active instruments
   - Inner join on key fields
   - Drop rows with unmatched or invalid instruments
4. **Log all drops** (if `track_dropped_rows=True`)
5. **Expose results** via `.get_clean_data()` and `.summary()`

---

## 🧪 Testing & Coverage

Unit tests are written using `pytest` and stored in `tests/test_cleaner.py`.

They cover:
- ✅ Successful retention of clean rows
- ✅ Drop logic for malformed rows
- ✅ Duplicate and whitespace cleanup
- ✅ Exception handling when using the class improperly
- ✅ Missing required columns

To run:
```bash
PYTHONPATH=src pytest -v
```

---

## 🧩 Edge Case Handling

- ✅ Missing/invalid price or date fields
- ✅ Extra/empty/malformed rows
- ✅ Whitespace and duplicates
- ✅ Reference mismatches
- ✅ Fully empty rows
- ⚠️ CSV injection (e.g., `=CMD(...)`) not yet handled

---

## 📊 Evaluation & Future Work

### ✅ Efficiency
- Uses vectorized operations and batch parsing
- Fast for in-memory datasets up to ~10M rows

### 🔧 Improvements Suggested
- Export to CSV/Parquet with formula-safe escaping
- Redact sensitive info in logs
- Add ability to replace missing Exchange field based on reference data (if uniquely identifiable by Symbol + InstrumentType)
- Add CLI or stream processing support
- Track detailed rejection stats (percent dropped, etc.)

---

## 📁 Files

- `main.txt` – Entry point for execution
- `src/cleaner/cleaner.py` – Main logic
- `src/cleaner/logger_config.py` – Logging setup
- `tests/test_cleaner.py` – Full test suite
- `requirements.txt` – Dependencies
- `data/*.csv` – Sample input files

---

## 🚀 How to Run

1. Python 3.12+ required  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run:
   ```bash
   python main.txt
   ```

---

## 🏁 Conclusion

This solution represents a robust, extensible, and well-documented approach to financial data ingestion.  
Key strengths include:

- Transparent logic with clear assumptions
- Structured logging for auditing
- Full test coverage with meaningful assertions
- OOP architecture aligned with the problem's intent
- Scalable path for future productionization

---

**Author:** Alex Eygenson