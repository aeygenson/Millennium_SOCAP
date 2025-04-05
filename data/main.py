from cleaner.cleaner import MarketDataCleaner
from cleaner.logger_config import logger

def main():
    logger.info("Starting market data cleaning pipeline.")

    market_data_path = "data/financial_market_data.csv"
    reference_data_path = "data/instrument_reference.csv"

    cleaner = MarketDataCleaner()
    cleaner.load_data(market_data_path, reference_data_path)
    cleaner.clean()

    cleaned_df = cleaner.get_clean_data()
    logger.info(f"Cleaned data shape: {cleaned_df.shape}")

    # Optionally export or display
    cleaned_df.head().to_csv("cleaned_output_preview.csv", index=False)
    logger.info("Preview of cleaned data saved to 'cleaned_output_preview.csv'.")

if __name__ == "__main__":
    main()
