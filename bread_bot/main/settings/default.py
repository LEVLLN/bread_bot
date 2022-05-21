import json
import math
import os

# App
APP_NAME = os.getenv('APP_NAME', 'bread_bot')
ENVIRONMENT = os.getenv('ENV', 'LOCAL')
APP_VERSION = os.getenv('VERSION', '1.0.0')
DEBUG = os.getenv('DEBUG', 'false') == 'true'
APP_MODULES = [
    'auth',
    'telegramer',
]
# Uvicorn
PORT = int(os.getenv('PORT', 8080))
WORKERS_COUNT = int(os.getenv('WORKERS_COUNT', 1))
SERVER_RELOAD = DEBUG

# DB
DB_MAX_POOL = int(os.getenv('DB_MAX_POOL', 20))
DB_POOL_SIZE = max(math.ceil(DB_MAX_POOL / WORKERS_COUNT), 1)
DB_POOL_MAX_OVERFLOW = 0

DATABASE_SETTINGS = {
    'default': {
        'database': os.getenv('DB_NAME', 'bread_bot'),
        'user': os.getenv('DB_USER', 'bread_bot'),
        'password': os.getenv('DB_PASSWORD', 'bread_bot'),
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': os.getenv('DB_PORT', '5432'),
    }
}

DATABASE_URI = 'postgresql+psycopg2://' \
               '{user}:{password}@{host}:{port}/{database}' \
    .format(**DATABASE_SETTINGS['default'])
ASYNC_DATABASE_URI = 'postgresql+asyncpg://' \
                     '{user}:{password}@{host}:{port}/{database}' \
    .format(**DATABASE_SETTINGS['default'])

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'some_secret_key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CORS_ALLOW_ORIGINS = json.dumps(
    os.getenv('CORS_ALLOW_ORIGINS', '[localhost:8000,localhost:8080]'))

# Logging
ENABLE_TELEMETRY = os.getenv('ENABLE_TELEMETRY', 'true') == 'true'
LOG_DATE_FMT = '%Y-%m-%d %H:%M:%S'

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'logging.Formatter',
            'fmt': '%(levelname)s %(asctime)s %(message)s %(requests)s',
            'datefmt': LOG_DATE_FMT,

        },
        'json': {
            '()': 'bread_bot.utils.json_logger.JSONLogFormatter',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'json': {
            'formatter': 'json',
            'class': 'asynclog.AsyncLogDispatcher',
            'func': 'bread_bot.utils.json_logger.write_log',
        },
    },
    'loggers': {
        'bread_bot': {
            'handlers': ['json'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'sqlalchemy.engine.Engine': {
            'handlers': ['json'],
            'level': 'INFO' if DEBUG else 'ERROR',
            'propagate': False,
        },
        'uvicorn': {
            'handlers': ['json'],
            'level': 'INFO',
            'propagate': False,
        },
        'uvicorn.access': {
            'handlers': ['json'],
            'level': 'ERROR',
            'propagate': False,
        },
        'main.webserver': {
            'handlers': ['json'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        }
    },
}
# Mask of sensitive data
DEFAULT_SENSITIVE_KEY_WORDS = (
    'password',
    'email',
    'token',
    'Authorization',
    'first_name',
    'last_name',
    'csrftoken',
    'api_key',
    'ctn',
    'phone',
)

AUTO_MASK_LOGS = os.getenv('AUTO_MASK_LOGS', 'false') == 'true'
DEFAULT_SENSITIVE_KEY_WORDS_PATTERN = '|'.join(
    map(
        lambda x: f'\\b{x}\\b',
        DEFAULT_SENSITIVE_KEY_WORDS
    )
)
# Telegramer
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
NGROK_HOST = os.getenv('NGROK_HOST', 'localhost:8080')
SHOW_STR_LIMIT = int(os.getenv("SHOW_STR_LIMIT", 100))
MESSAGE_LEN_LIMIT = int(os.getenv("MESSAGE_LEN_LIMIT", 2500))
