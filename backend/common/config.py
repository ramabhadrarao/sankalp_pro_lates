import os
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv

# Load env from project root and backend/.env explicitly
# First try current working dir (.env in repo root)
load_dotenv(find_dotenv(usecwd=True), override=False)
# Then load backend/.env relative to this file
backend_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env, override=True)

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DB = os.getenv("MYSQL_DB", "salahkaarpro")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "salahkaarpro")

JWT_SECRET = os.getenv("JWT_SECRET", "insecure-dev-secret-change-me")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
REFRESH_EXPIRES_MINUTES = int(os.getenv("REFRESH_EXPIRES_MINUTES", "43200"))  # 30 days

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
SUBSCRIPTION_SERVICE_URL = os.getenv("SUBSCRIPTION_SERVICE_URL", "http://localhost:8003")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
CALCULATION_SERVICE_URL = os.getenv("CALCULATION_SERVICE_URL", "http://localhost:8005")
REPORT_SERVICE_URL = os.getenv("REPORT_SERVICE_URL", "http://localhost:8006")
FORM_SERVICE_URL = os.getenv("FORM_SERVICE_URL", "http://localhost:8007")
AFFILIATE_SERVICE_URL = os.getenv("AFFILIATE_SERVICE_URL", "http://localhost:8008")
ADMIN_SERVICE_URL = os.getenv("ADMIN_SERVICE_URL", "http://localhost:8009")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8010")
STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://localhost:8011")
I18N_SERVICE_URL = os.getenv("I18N_SERVICE_URL", "http://localhost:8012")
PRO_SERVICE_URL = os.getenv("PRO_SERVICE_URL", "http://localhost:8013")


def mysql_url() -> str:
    # URL-encode credentials to support special characters like '@' or ':'
    user_enc = quote_plus(MYSQL_USER)
    pass_enc = quote_plus(MYSQL_PASSWORD)
    return f"mysql+pymysql://{user_enc}:{pass_enc}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"