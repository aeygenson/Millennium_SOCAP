import pandas as pd
from cleaner.logger_config import logger

class MarketDataCleaner:
    def __init__(self, validate_active_only: bool = True, track_dropped_rows: bool = False, fix_dot_in_symbol: bool = False):
        # Configuration flags
        self.validate_active_only = validate_active_only
        self.track_dropped_rows = track_dropped_rows
        self.fix_dot_in_symbol = fix_dot_in_symbol

        # Data placeholders
        self.market_df = None
        self.instrument_df = None
        self.cleaned_df = None

    def load_data(self, market_data_path: str, reference_data_path: str):
        # Load raw market and reference data
        logger.info("Loading market and reference data...")
        self.market_df = pd.read_csv(market_data_path)
        self.instrument_df = pd.read_csv(reference_data_path)
        logger.info(f"Loaded market data: {len(self.market_df)} rows")
        logger.info(f"Loaded reference data: {len(self.instrument_df)} rows")

    def clean(self):
        # Ensure data is loaded
        if self.market_df is None or self.instrument_df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        df = self.market_df.copy()

        # Normalize string fields
        df['Symbol'] = df['Symbol'].astype(str).str.strip()
        df['InstrumentType'] = df['InstrumentType'].astype(str).str.strip()
        df['Exchange'] = df['Exchange'].astype(str).str.strip()

        # Replace empty strings in Exchange with NaN for fillna to work
        df['Exchange'] = df['Exchange'].replace('', pd.NA)

        # Fix SYMBOL.EXCHANGE pattern if configured
        if self.fix_dot_in_symbol:
            fix_count = 0
            for idx, row in df.iterrows():
                if '.' in row['Symbol']:
                    parts = row['Symbol'].rsplit('.', 1)
                    if len(parts) == 2:
                        symbol_part, exchange_part = parts
                        if symbol_part and exchange_part:
                            logger.info(f"Fixing dot-in-symbol at row {idx}: {row['Symbol']} → Symbol={symbol_part}, Exchange={exchange_part}")
                            df.at[idx, 'Symbol'] = symbol_part
                            df.at[idx, 'Exchange'] = exchange_part
                            fix_count += 1
            logger.info(f"Dot-in-symbol corrections applied: {fix_count} rows")

        # Drop empty and duplicate rows
        df.dropna(how='all', inplace=True)
        df.drop_duplicates(inplace=True)

        # Convert price fields to numeric
        price_cols = ['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        df['OpenInterest'] = pd.to_numeric(df['OpenInterest'], errors='coerce')

        # Drop rows with critical missing price or date
        df_valid = df.dropna(subset=price_cols + ['Date'])
        if self.track_dropped_rows:
            dropped = df[~df.index.isin(df_valid.index)]
            for _, row in dropped.iterrows():
                logger.warning(f"Dropped row due to missing price or date: {row.to_dict()}")
        df = df_valid

        # Parse and filter invalid dates
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'].notnull()]

        # Filter reference data
        ref = self.instrument_df.copy()
        if self.validate_active_only:
            ref = ref[ref['Status'] == 'Active']

        # Normalize reference fields
        self.instrument_df['Symbol'] = self.instrument_df['Symbol'].astype(str).str.strip()
        self.instrument_df['InstrumentType'] = self.instrument_df['InstrumentType'].astype(str).str.strip()

        # Validate against reference
        pre_merge_count = len(df)
        validated = df.merge(ref[['Symbol', 'InstrumentType', 'Exchange']], on=['Symbol', 'InstrumentType', 'Exchange'], how='inner')
        if self.track_dropped_rows:
            unmatched = df[~df.set_index(['Symbol', 'InstrumentType', 'Exchange']).index.isin(
                validated.set_index(['Symbol', 'InstrumentType', 'Exchange']).index)]
            for _, row in unmatched.iterrows():
                logger.warning(f"Dropped row due to invalid instrument reference: {row.to_dict()}")

        logger.info(f"Rows after validation: {len(validated)} / {pre_merge_count}")
        self.cleaned_df = validated.reset_index(drop=True)

    def get_clean_data(self) -> pd.DataFrame:
        # Return the cleaned dataset
        if self.cleaned_df is None:
            raise ValueError("Data has not been cleaned yet. Call clean() first.")
        return self.cleaned_df.copy()

    def summary(self):
        # Print summary stats and missing data info
        if self.cleaned_df is None:
            raise ValueError("Data has not been cleaned yet. Call clean() first.")

        logger.info("Data Summary:")
        logger.info(self.cleaned_df.describe(include='all'))
        logger.info("Missing Values:")
        logger.info(self.cleaned_df.isnull().sum())
