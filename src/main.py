from cleaner.cleaner import MarketDataCleaner
from cleaner.logger_config import logger

# Paths to input CSV files (update as needed)
MARKET_DATA_PATH = "data/financial_market_data.csv"
REFERENCE_DATA_PATH = "data/instrument_reference.csv"

# Initialize the cleaner
cleaner = MarketDataCleaner(
    validate_active_only=True,
    track_dropped_rows=True
)

# Load and clean data
logger.info("Starting market data cleaning pipeline...")
cleaner.load_data(MARKET_DATA_PATH, REFERENCE_DATA_PATH)
cleaner.clean()

# Output a summary of the cleaned data
cleaner.summary()

# Access the cleaned DataFrame
cleaned_data = cleaner.get_clean_data()

# Optionally export
output_path = "data/cleaned_output.csv"
cleaned_data.to_csv(output_path, index=False)
logger.info(f"✅ Cleaned data saved to {output_path}")
