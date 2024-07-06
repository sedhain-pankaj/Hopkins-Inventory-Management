import os

# Constants used in the program
FONT_SIZE = 70 if os.name == "nt" else 128

# Time delay in milliseconds for updating the time label
TIME_DELAY = 1000

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORNICE_RATE_FILEPATH = os.path.join(BASE_DIR, "assets", "cornice_rate.csv")
OVERALL_STOCK_FILEPATH = os.path.join(BASE_DIR, "assets", "overall_stock.csv")

