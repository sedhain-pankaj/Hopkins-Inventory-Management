import os

# Constants used in the program
FONT_SIZE = 70 if os.name == "nt" else 128

# Time delay in milliseconds for updating the time label
TIME_DELAY = 1000

# File path for the cornice rate csv file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILEPATH = os.path.join(BASE_DIR, "assets", "cornice_rate.csv")
