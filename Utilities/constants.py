import os

# Constants used in the program
FONT_SIZE = 70 if os.name == "nt" else 128

# Time delay in milliseconds for updating the time label
TIME_DELAY = 1000

# SHA-256 for the password
PASSWORD_HASH = "74327943f791e17b6081b590be47d518d885b79972d37087df480448e0672094"

# File paths - go up one directory level to get the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORNICE_RATE_FILEPATH = os.path.join(BASE_DIR, "assets", "cornice_rate.csv")
OVERALL_STOCK_FILEPATH = os.path.join(BASE_DIR, "assets", "overall_stock.csv")
