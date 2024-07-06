import os

# Constants used in the program
FONT_SIZE = 96 if os.name == "nt" else 128

# Time delay in milliseconds for updating the time label
TIME_DELAY = 1000

# File path for the cornice rate csv file
FILEPATH = os.path.join("assets", "cornice_rate.csv")
