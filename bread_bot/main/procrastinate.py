from procrastinate import AiopgConnector, App, testing

from bread_bot.main.settings import DATABASE_SETTINGS, ENVIRONMENT

db_settings = DATABASE_SETTINGS["default"]
if ENVIRONMENT == "TESTING":
    connector = testing.InMemoryConnector()
else:
    connector = AiopgConnector(host=db_settings["host"], user=db_settings["user"], password=db_settings["password"])
app = App(
    connector=connector,
    import_paths=["bread_bot.common.async_tasks"],
)
