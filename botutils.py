import sqlite3
from datetime import datetime

SET_SERVER_SETTING_SQL = "INSERT INTO Guild_Settings (Guild_ID, Setting, Value) VALUES (?, ?, ?) ON CONFLICT(Guild_ID, Channel_ID) DO UPDATE SET Value = ?"
GET_SERVER_SETTING_SQL = "SELECT Value FROM Guild_Settings WHERE Guild_ID = ? AND Setting = ?"


def initialize_database():
    CREATE_TABLE_GUILD_SETTINGS = '''
    CREATE TABLE IF NOT EXISTS "Guild Settings" (
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Guild_ID INTEGER NOT NULL,
        Setting TEXT(32) NOT NULL,
        Value TEXT(32) NOT NULL,
        CONSTRAINT Guild_Settings_UN UNIQUE (Guild_ID,Setting)
    )
    '''
    db = SQLite3Helper()
    sql_result = db.execute(CREATE_TABLE_GUILD_SETTINGS)


def initialize_table(sql_string_create):
    db = SQLite3Helper()
    sql_result = db.execute(sql_string_create)


# TODO: Fix set/get functions to not use rowcount, which is unreliable in SQLite
async def set_server_setting(guild_id, setting, value):
    db = SQLite3Helper()
    sql = SET_SERVER_SETTING_SQL
    val = (guild_id, setting, value, value)
    db.execute(sql, val)
    return db.rowcount


async def get_server_setting(guild_id, setting):
    db = SQLite3Helper()
    sql = GET_SERVER_SETTING_SQL
    val = (guild_id, setting)
    result = db.fetchone(sql, val)
    if db.rowcount == 1:
        value = result[0]
    else:
        value = None
    return value


def debug(_string):
    print(_string)


def timenow():
    return datetime.now().strftime('%Y/%m/%d %H:%M')


class SQLite3Helper:
    db = "bobobot.sqlite"

    def __init__(self):
        self.rowcount = None

    def __connect__(self):
        try:
            self.con = sqlite3.connect(self.db)
        except sqlite3.Error as err:
            print('Cannot connect to database.', err)
            exit()
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql, val=None):
        self.__connect__()
        if val:
            self.cur.execute(sql, val)
        else:
            self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def fetchone(self, sql, val=None):
        self.__connect__()
        try:
            if val:
                self.cur.execute(sql, val)
            else:
                self.cur.execute(sql)
        except AttributeError as err:
            print(err)
        result = self.cur.fetchone()
        self.__disconnect__()
        return result

    # TODO: Fix to not use rowcount
    def execute(self, sql, val=None):
        self.__connect__()
        try:
            if val:
                self.cur.execute(sql, val)
            else:
                self.cur.execute(sql)
        except sqlite3.Error as err:
            print(err)
            raise
        self.con.commit()
        result = self.cur.rowcount
        self.__disconnect__()
        return result

