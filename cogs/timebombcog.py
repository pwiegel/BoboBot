# timebombcog.py
# Data stored: Guild ID, Channel ID, User ID, Message ID
# Permissions needed: READ_MESSAGES, SEND_MESSAGES, READ_MESSAGE_HISTORY, MANAGE_MESSAGES

import botutils
from bot import bobobot
from botconfig import COMMAND_PREFIX
from discord.ext import tasks, commands
from discord import errors
from datetime import datetime, timedelta
from sys import exc_info

TIMEBOMB_SET_SQL = "INSERT INTO Timebomb (Bomb_Time, Guild_ID, Channel_ID, Author_ID, Message_ID) VALUES (?,?,?,?,?)"
TIMEBOMB_REMOVE_SQL = "DELETE FROM Timebomb WHERE Message_ID = ?"
TIMEBOMB_EXPLODE_SQL = "SELECT Message_ID, Channel_ID FROM Timebomb WHERE Bomb_Time < datetime('now', 'localtime')"
TIMEBOMB_EXPLODE_ALL_SQL = "SELECT Message_ID, Channel_ID FROM Timebomb"
TIMEBOMB_EXPLODE_MINE_SQL = "SELECT Message_ID, Channel_ID FROM Timebomb WHERE Author_ID = ?"

# Create the Timebomb table if it does not exist
CREATE_TABLE_TIMEBOMB = '''
    CREATE TABLE IF NOT EXISTS Timebomb (
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Bomb_Time TEXT NOT NULL,
        Guild_ID INTEGER NOT NULL,
        Channel_ID INTEGER NOT NULL,
        Author_ID INTEGER NOT NULL,
        Message_ID INTEGER NOT NULL
    )
'''

# Create the Timebomb table, if it does not exist
botutils.initialize_table(CREATE_TABLE_TIMEBOMB)


def setup(bot):
    bot.add_cog(TimebombCog(bot))


async def mysql_remove_bomb(message_id):
    """ Removes the specified message from the timebomb table.

    :parameter
    message_id : ID of the timebomb message to remove from the database

    :return
    db.rowcount : Number of rows deleted from the database. Should be 1 if delete was successful.
    """

    db = botutils.SQLite3Helper()
    sql = TIMEBOMB_REMOVE_SQL
    val = (message_id,)
    db.execute(sql, val)
    return db.cur.rowcount


async def explode(override=None, tauthor=None):
    """ Immediately trigger deletion of all timebombs in the scope specified by override.

    :parameter
    override : all - explode all currently set timebombs on the server
               mine - explode all currently set timebombs on the server for the current user
    :return
    No return value.
    """
    db = botutils.SQLite3Helper()
    val = None
    if 'all' == override:
        sql = TIMEBOMB_EXPLODE_ALL_SQL
    elif 'mine' == override:
        sql = TIMEBOMB_EXPLODE_MINE_SQL
        val = (tauthor,)
    else:
        sql = TIMEBOMB_EXPLODE_SQL

    if val:
        explodelist = db.fetch(sql, val)
    else:
        explodelist = db.fetch(sql)

    for row in explodelist:
        explode_id = row[0]
        explode_channel_id = row[1]
        explode_channel = bobobot.get_channel(explode_channel_id)
        explode_message = await explode_channel.fetch_message(explode_id)
        try:
            await explode_message.delete()
        except errors.NotFound as err:
            print(f'NotFound: Message ID {explode_id} not deleted.')
            print(err)
            return None
        except errors.Forbidden as err:
            print(f'Forbidden: Message ID {explode_id} not deleted.')
            print(err)
            return None
        except errors.ClientException as err:
            print(f'ClientException: Message ID {explode_id} not deleted.')
            print(err)
            return None
        except errors.DiscordException as err:
            print(f'DiscordException: Message ID {explode_id} not deleted.')
            print(err)
            return None
        except Exception:
            print('Generic exception.', exc_info())
            return None

        print(f'Message successfully deleted. Removing {explode_id} from the database.')
        mysql_remove_bomb_rowcount = await mysql_remove_bomb(explode_id)
        if mysql_remove_bomb_rowcount != 1:
            print(f'Message ID {explode_id} was not removed from the database. rc: {mysql_remove_bomb_rowcount}')


class TimebombCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.explode_loop.start()

    @tasks.loop(minutes=1)
    async def explode_loop(self):
        await explode()

    @explode_loop.before_loop
    async def before_purge_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name='explodeall', hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def explodeall(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}explodeall called by {ctx.author.display_name}')
        await explode('all')
        await ctx.message.delete()

    @commands.command(name='explodemine')
    async def explodemine(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}explodemine called by {ctx.author.display_name}')
        await explode('mine', str(ctx.author))
        await ctx.message.delete()

    @commands.command(name='timebomb')
    async def timebomb(self, ctx, *, arg):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}timebomb {arg} called by {ctx.author.display_name}')

        # Get the last word of the message string, which will be the timer to delete the message, then split that
        # word into a number with a letter (example: 30m), then split the letter from the number
        tb_time = arg.split()[-1]
        tb_unit = tb_time[-1:]
        tb_num_units = float(tb_time[:-1])
        tb_diff = None

        if 'm' == tb_unit:
            print(f'Exploding in {tb_num_units} Minutes(s)')
            tb_diff = timedelta(minutes=tb_num_units)
        elif 'h' == tb_unit:
            print(f'Exploding in {tb_num_units} Hours(s)')
            tb_diff = timedelta(hours=tb_num_units)
        elif 'd' == tb_unit and 45 > tb_unit:
            print(f'Exploding in {tb_num_units} Days(s)')
            tb_diff = timedelta(days=tb_num_units)
        else:
            print('Invalid time frame.')

        tb_explode_time = datetime.now() + tb_diff

        # Do the database thing
        db = botutils.SQLite3Helper()
        val = (tb_explode_time, ctx.message.guild.id, ctx.channel.id, str(ctx.author), ctx.message.id)
        db.execute(TIMEBOMB_SET_SQL, val)
        print(f"{db.cur.rowcount} time bomb set for message id {ctx.message.id} in server {ctx.message.guild.id}.")



