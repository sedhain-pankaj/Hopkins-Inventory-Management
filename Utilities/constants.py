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

# Local application data. Fingerprint templates are deliberately kept out of
# fprintd/PAM so this app does not enroll fingerprints for OS login.
DATA_DIR = os.path.join(BASE_DIR, "data")
EMPLOYEE_REGISTRY_FILEPATH = os.path.join(DATA_DIR, "employees.csv")
TIME_CLOCK_LOG_FILEPATH = os.path.join(DATA_DIR, "time_clock_log.csv")
FINGERPRINT_STORAGE_DIR = os.path.join(DATA_DIR, "fingerprints")
FINGERPRINT_HELPER_ENV = "HPS_FINGERPRINT_HELPER"
