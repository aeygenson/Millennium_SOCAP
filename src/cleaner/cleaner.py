import pandas as pd
from cleaner.logger_config import logger

class MarketDataCleaner:
    def __init__(self, validate_active_only: bool = True, track_dropped_rows: bool = False):
        # Initialize configuration flags and internal data containers
        self.market_df = None
        self.instrument_df = None
        self.cleaned_df = None
        self.validate_active_only = validate_active_only  # Whether to restrict validation to active instruments only
        self.track_dropped_rows = track_dropped_rows      # Whether to log each dropped row in detail

    def load_data(self, market_data_path: str, reference_data_path: str):
        # Load raw market data and reference instrument definitions from CSV files
        logger.info("Loading market and reference data...")
        self.market_df = pd.read_csv(market_data_path)
        self.instrument_df = pd.read_csv(reference_data_path)
        logger.info(f"Market data rows: {len(self.market_df)}")
        logger.info(f"Reference data rows: {len(self.instrument_df)}")

    def clean(self):
        # Ensure data is loaded before cleaning
        if self.market_df is None or self.instrument_df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Copy market data to avoid modifying the original
        df = self.market_df.copy()

        # Trim whitespace in string identifier fields
        df['Symbol'] = df['Symbol'].astype(str).str.strip()
        df['InstrumentType'] = df['InstrumentType'].astype(str).str.strip()
        df['Exchange'] = df['Exchange'].astype(str).str.strip()

        # Remove empty and duplicate rows
        df.dropna(how='all', inplace=True)
        df.drop_duplicates(inplace=True)

        # Convert key price and volume fields to numeric, coercing errors to NaN
        price_cols = ['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        df['OpenInterest'] = pd.to_numeric(df['OpenInterest'], errors='coerce')

        # Drop rows missing critical price data or date
        df_price_valid = df.dropna(subset=price_cols + ['Date'])
        dropped_price_rows = df[~df.index.isin(df_price_valid.index)]
        if self.track_dropped_rows:
            for _, row in dropped_price_rows.iterrows():
                logger.warning(f"Dropped row due to missing price data or date: {row.to_dict()}")
        df = df_price_valid

        # Parse date column to datetime format, drop rows with unparseable dates
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        dropped_date_rows = df[df['Date'].isnull()]
        if self.track_dropped_rows:
            for _, row in dropped_date_rows.iterrows():
                logger.warning(f"Dropped row due to invalid date format: {row.to_dict()}")
        df = df[df['Date'].notnull()]

        logger.info(f"Rows after cleaning: {len(df)}")

        # Copy reference data and optionally filter to only active instruments
        ref = self.instrument_df.copy()
        if self.validate_active_only:
            ref = ref[ref['Status'] == 'Active']

        # Perform validation via inner join on Symbol, InstrumentType, and Exchange
        pre_merge_rows = len(df)
        validated_df = df.merge(ref[['Symbol', 'InstrumentType', 'Exchange']],
                                on=['Symbol', 'InstrumentType', 'Exchange'],
                                how='inner')

        # Log rows that failed reference validation if enabled
        dropped_merge_df = df[~df.set_index(['Symbol', 'InstrumentType', 'Exchange']).index.isin(
            validated_df.set_index(['Symbol', 'InstrumentType', 'Exchange']).index)]
        if self.track_dropped_rows:
            for _, row in dropped_merge_df.iterrows():
                logger.warning(f"Dropped row due to invalid instrument reference: {row.to_dict()}")

        df = validated_df
        logger.info(f"Rows after reference validation: {len(df)} (dropped {pre_merge_rows - len(df)} rows)")

        # Save cleaned data for downstream access
        self.cleaned_df = df.reset_index(drop=True)

    def get_clean_data(self) -> pd.DataFrame:
        # Return cleaned dataset or raise if not yet processed
        if self.cleaned_df is None:
            raise ValueError("Data has not been cleaned yet. Call clean() first.")
        return self.cleaned_df.copy()

    def summary(self):
        # Print summary statistics and missing data info for the cleaned dataset
        if self.cleaned_df is None:
            raise ValueError("Data has not been cleaned yet. Call clean() first.")

        logger.info("Summary of cleaned data:")
        logger.info(self.cleaned_df.describe(include='all'))

        logger.info("Missing values per column:")
        logger.info(self.cleaned_df.isnull().sum())
