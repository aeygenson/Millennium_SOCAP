import logging

logger = logging.getLogger("MarketDataCleaner")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(ch)

file_handler = logging.FileHandler('market_cleaner.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)