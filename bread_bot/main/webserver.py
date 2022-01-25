import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opencensus.trace.samplers import AlwaysOnSampler

from bread_bot.auth.routes import auth
from bread_bot.main import routes as root
from bread_bot.main.settings import CORS_ALLOW_ORIGINS, LOG_CONFIG, \
    ENABLE_TELEMETRY
from bread_bot.telegramer.routes import telegram
from bread_bot.utils.middlewares import OpenCensusFastAPIMiddleware, \
    LoggingMiddleware

dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(
    LoggingMiddleware()
)
if ENABLE_TELEMETRY:
    app.middleware('http')(
        OpenCensusFastAPIMiddleware(app, sampler=AlwaysOnSampler())
    )
# Routes
app.include_router(auth.router)
app.include_router(root.router)
app.include_router(telegram.router)
