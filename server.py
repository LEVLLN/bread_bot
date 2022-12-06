import uvicorn

from bread_bot.main.settings import (
    APP_NAME,
    PORT,
    WORKERS_COUNT,
    SERVER_RELOAD,
)

if __name__ == "__main__":
    uvicorn.run(
        f"{APP_NAME}.main.webserver:app",
        host="0.0.0.0",
        port=PORT,
        reload=SERVER_RELOAD,
        workers=WORKERS_COUNT,
        access_log=False,
    )
