# purgecog.py
# Data stored: Guild ID, Channel ID
# Permissions needed: READ_MESSAGES, SEND_MESSAGES, READ_MESSAGE_HISTORY, MANAGE_MESSAGES

import botutils
from bot import bobobot
from botconfig import COMMAND_PREFIX
import discord
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from sys import exc_info

PURGE_GET_GUILD_LIST_SQL = "SELECT DISTINCT Guild_ID FROM Purge_Channels"
PURGE_GET_CHANNEL_SETTING_SQL = "SELECT Purge_Time FROM Purge_Channels WHERE Guild_ID = ? AND Channel_id = ?"
PURGE_GET_CHANNEL_LIST_SQL = "SELECT Channel_ID, Purge_Time FROM Purge_Channels WHERE Guild_ID = ?"
PURGE_SET_CHANNEL_SQL = "INSERT INTO Purge_Channels (Guild_ID, Channel_ID, Purge_time) VALUES (?, ?, ?) ON CONFLICT(Guild_ID, Channel_ID) DO UPDATE SET Purge_Time = ?"
PURGE_REMOVE_CHANNEL_SQL = "DELETE FROM Purge_Channels WHERE Guild_ID = ? AND Channel_ID = ?"

CREATE_TABLE_PURGE_CHANNEL = '''
    CREATE TABLE IF NOT EXISTS Purge_Channels (
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Guild_ID INTEGER NOT NULL,
        Channel_ID INTEGER NOT NULL,
        Purge_Time TEXT NOT NULL,
        CONSTRAINT Purge_Channels_UN UNIQUE (Guild_ID, Channel_ID)
    )
'''

# Create the Purge_Channels table, if it does not exist
botutils.initialize_table(CREATE_TABLE_PURGE_CHANNEL)


def setup(bot):
    bot.add_cog(PurgeCog(bot))


async def get_purge_channel_list(guild_id):
    db = botutils.SQLite3Helper()
    return dict(db.fetch(PURGE_GET_CHANNEL_LIST_SQL, (guild_id,)))


async def get_purge_channel_setting(guild_id, channel_id):
    db = botutils.SQLite3Helper()
    return db.fetch(PURGE_GET_CHANNEL_SETTING_SQL, (guild_id, channel_id))


async def remove_purge_channel(guild_id, channel_id):
    db = botutils.SQLite3Helper()
    db.execute(PURGE_REMOVE_CHANNEL_SQL, (guild_id, channel_id))
    return db.rowcount


async def set_purge_channel(guild_id, channel_id, purge_time):
    db = botutils.SQLite3Helper()
    db.execute(PURGE_SET_CHANNEL_SQL, (guild_id, channel_id, purge_time, purge_time))


async def get_purge_guild_list():
    db = botutils.SQLite3Helper()
    return db.fetch(PURGE_GET_GUILD_LIST_SQL)


async def purge_guild_channels(guild_id):
    # Get the Discord guild object, query sql for a dict of channel IDs and purge settings for this guild
    discord_purge_guild = bobobot.get_guild(guild_id)
    purge_channel_list = await get_purge_channel_list(discord_purge_guild.id)
    for purge_channel_id in purge_channel_list:
        purge_active = True
        messages_purged = None
        purge_diff = None

        # parse the setting, then get a timedelta from it, then get a datetime to purge before
        purge_channel_time = purge_channel_list[purge_channel_id]
        purge_num = int(purge_channel_time[:-1])
        purge_units = purge_channel_time[-1:]
        time_now_utc = datetime.utcnow()
        purge_start_time = time_now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        purge_end_time = time_now_utc.replace(hour=0, minute=11, second=0, microsecond=0)

        if purge_units == 'm':
            purge_diff = timedelta(minutes=purge_num)
        elif purge_units == 'h':
            purge_diff = timedelta(hours=purge_num)
        elif purge_units == 'd':
            purge_diff = timedelta(days=purge_num)
            if not purge_start_time < time_now_utc < purge_end_time:
                purge_active = False

        purge_time = time_now_utc - purge_diff
        # TODO handle deleted / non-existent channels
        discord_purge_channel = discord.utils.get(discord_purge_guild.channels, id=purge_channel_id)
        try:
            if purge_active:
                messages_purged = await discord_purge_channel.purge(limit=100, before=purge_time)
        except discord.errors.NotFound as err:
            print(f'Channel Not Found: {discord_purge_channel.name} ({discord_purge_channel.id})')
            print(err)
        except discord.errors.Forbidden as err:
            print(f'Forbidden: Cannot purge: {discord_purge_channel.name} ({discord_purge_channel.id}).')
            print(err)
        except discord.HTTPException as err:
            print(f'Error while purging {discord_purge_channel.name} ({discord_purge_channel.id}).')
            print(err)
        except discord.errors.DiscordException as err:
            print(f'Error while purging {discord_purge_channel.name} ({discord_purge_channel.id}).')
            print(err)
        except:
            print(f'Error while purging {discord_purge_channel.name} ({discord_purge_channel.id}).')
            print('Generic exception.', exc_info())


class PurgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.purge_loop.start()

    @tasks.loop(minutes=1)
    async def purge_loop(self):
        purge_guild_id_list = await get_purge_guild_list()
        for purge_guild_id in purge_guild_id_list:
            await purge_guild_channels(purge_guild_id[0])

    @purge_loop.before_loop
    async def before_purge_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name='removepurge')
    @commands.has_permissions(manage_guild=True)
    async def removepurge(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}removepurge called by {ctx.author.display_name}')
        remove_purge_channel_result = await remove_purge_channel(ctx.guild.id, ctx.channel.id)
        if remove_purge_channel_result == 1:
            print(f"removepurge(): rowcount: {remove_purge_channel_result}")
            await ctx.send(f'Purge removed for #{ctx.channel.name}')
        elif remove_purge_channel_result == 0:
            print(f"removepurge(): rowcount: {remove_purge_channel_result}")
            await ctx.send(f'No purge was set for #{ctx.channel.name}')

    @commands.command(name='showpurge')
    @commands.has_permissions(manage_guild=True)
    async def showpurge(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}showpurge called by {ctx.author.display_name}')
        channel_setting_results = await get_purge_channel_setting(ctx.guild.id, ctx.channel.id)
        channel_purge_setting_list = [x[0] for x in channel_setting_results]
        try:
            channel_purge_setting = channel_purge_setting_list[0]
        except IndexError:
            await ctx.send(f'#{ctx.channel.name} has no purge setting.')
            return
        purge_units = channel_purge_setting[-1:]
        purge_num_units = channel_purge_setting[:-1]
        await ctx.send(f'#{ctx.channel.name} is set to purge every {purge_num_units} {purge_units}')

    @commands.command(name='setpurge')
    @commands.has_permissions(manage_guild=True)
    async def setpurge(self, ctx, arg):
        print(f"{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}setpurge {arg} called by {ctx.author.display_name}")
        try:
            purge_num_units = int(arg[:-1])
        except ValueError:
            purge_num_units = 9999

        if arg.endswith('m') and purge_num_units < 999:
            purge_units = 'm'
        elif arg.endswith('h') and purge_num_units < 312:
            purge_units = 'h'
        elif arg.endswith('d') and purge_num_units < 14:
            purge_units = 'd'
        else:
            await ctx.send(f'{arg} is not a valid setting. Valid time units are m/h/d. Max values: 999m, 312h, 14d')
            return

        await set_purge_channel(ctx.guild.id, ctx.channel.id, arg)
        await ctx.send(f'#{ctx.channel.name} is set to purge every {purge_num_units} {purge_units}')

    @commands.command(name='purge', hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def purge(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}purge called by {ctx.author.display_name}')
        await purge_guild_channels(ctx.guild.id)

    @commands.command(name='purgeall', hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def purgeall(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}purgeall called by {ctx.author.display_name}')
        purge_guild_list = await get_purge_guild_list()
        for purge_guild_id in purge_guild_list:
            await purge_guild_channels(purge_guild_id[0])
