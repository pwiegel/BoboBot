# botconfig.py
# Prior to running the bot, config.ini must be configured by adding your Discord bot token to config_template.ini and
# renaming it to config.ini.
# If using the Imgur cog, you must also provide Imgur Client ID and Client Secret strings.

import configparser
import botutils

config = configparser.ConfigParser()
config.read(f'config.ini')

COMMAND_PREFIX = config.get('BOBOBOT', 'COMMAND_PREFIX')
SQLITE_DB = config.get('SQLITE', 'SQLITE_DB')
DISCORD_TOKEN = config.get('DISCORD', 'DISCORD_TOKEN')
IMGUR_CLIENT_ID = config.get('IMGUR', 'IMGUR_CLIENT_ID')
IMGUR_CLIENT_SECRET = config.get('IMGUR', 'IMGUR_CLIENT_SECRET')

CREATE_TABLE_GUILD_SETTINGS = '''
CREATE TABLE IF NOT EXISTS "Guild_Settings" (
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Guild_ID INTEGER NOT NULL,
    Setting TEXT(32) NOT NULL,
    Value TEXT(32) NOT NULL,
    CONSTRAINT Guild_Settings_UN UNIQUE (Guild_ID,Setting)
)
'''

# Create the SQLite database if it does not exist, then create the Guild_Settings table if it does not exist.
botutils.initialize_database()
botutils.initialize_table(CREATE_TABLE_GUILD_SETTINGS)
