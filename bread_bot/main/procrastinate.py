from procrastinate import AiopgConnector, App

from bread_bot.main.settings import DATABASE_SETTINGS

db_settings = DATABASE_SETTINGS["default"]
app = App(
    connector=AiopgConnector(host=db_settings["host"], user=db_settings["user"], password=db_settings["password"]),
    import_paths=["bread_bot.common.async_tasks"],
)
app.open()
