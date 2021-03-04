# memberchannel.py
# Data stored: Guild ID, User ID, User Nickname, Channel ID
# Permissions needed: ADMINISTRATOR (Some functionality with managing channels and categories is not included with
# MANAGE_CHANNELS or MANAGE_GUILD. Needs further testing.)
# TODO: Re-test completed cog for specific permission requirements

import re
import sys
import discord
import botutils
from discord.ext import commands
from botconfig import COMMAND_PREFIX
from bot import bobobot

MC_CAT_NAME_SETTING = 'MC_Cat_Name'
MEMBER_CHANNEL_SET_SQL = "INSERT INTO Member_Channel (Guild_ID, Author_ID, Author_Nick, Channel_ID) VALUES (?, ?, ?, ?)"
MEMBER_CHANNEL_GET_ID_SQL = "SELECT Channel_ID FROM Member_Channel WHERE Guild_ID = ? AND Author_ID = ?"
MEMBER_CHANNEL_GET_OWNER_SQL = "SELECT Author_ID, Author_Nick FROM Member_Channel WHERE Guild_ID = ? AND Channel_ID = ?"
MEMBER_CHANNEL_DELETE_SQL = "DELETE FROM Member_Channel WHERE Channel_ID = ?"

CREATE_TABLE_MEMBER_CHANNEL = '''
CREATE TABLE IF NOT EXISTS Member_Channel (
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Guild_ID INTEGER NOT NULL,
    Author_ID TEXT NOT NULL,
    Author_Nick TEXT NOT NULL,
    Channel_ID INTEGER NOT NULL,
    CONSTRAINT Member_Channel_UN UNIQUE (Guild_ID, Author_ID)
)
'''

# Create the Member_Channel table, if it does not exist.
botutils.initialize_table(CREATE_TABLE_MEMBER_CHANNEL)


def setup(bot):
    bot.add_cog(MemberChannelCog(bot))


def safe_nick(nick):
    if not nick:
        request_nick = nick.lower()
    else:
        request_nick = nick.lower()
        request_nick = request_nick.replace(' ', '_')
    pattern = re.compile(r'[^\w\s]+', re.UNICODE)
    safenick = re.sub(pattern, '', request_nick)
    return safenick


async def sort_cat(ctx, unsorted_category):
    # TODO Smarter sorting; maintain same set of position values, but reassign them to sorted channels
    discord_category = discord.utils.get(ctx.guild.categories, name=unsorted_category)
    position_index = 101
    channel_dict = {}
    if not discord_category:
        print(f'Category {unsorted_category} not found.')
        for discord_category in ctx.guild.categories:
            print(discord_category.name)
    else:
        for discord_channel in discord_category.channels:
            channel_dict[discord_channel.name] = discord_channel.position
    channel_dict_items = channel_dict.items()
    channel_dict_sorted = sorted(channel_dict_items)

    print(f'Sorting {discord_category.name}')
    for dict_key, dict_value in channel_dict_sorted:
        try:
            discord_channel = discord.utils.get(discord_category.channels, name=dict_key)
        except Exception:
            print('Generic exception.', sys.exc_info())
            return

        if not discord_channel:
            print(f'Failed to get discord object for: {dict_key}')
        await discord_channel.edit(position=position_index)
        position_index = position_index + 1


async def get_member_channel_owner(guild_id, channel_id):
    db = botutils.SQLite3Helper()
    sql = MEMBER_CHANNEL_GET_OWNER_SQL
    val = (guild_id, channel_id)
    result = db.fetchone(sql, val)
    if result is not None:
        author_id = result[0]
        author_nick = result[1]
    else:
        author_id = None
        author_nick = None
    return author_id, author_nick


async def get_member_channel_id(guild_id, member_id):
    db = botutils.SQLite3Helper()
    sql = MEMBER_CHANNEL_GET_ID_SQL
    val = (guild_id, member_id)
    result = db.fetchone(sql, val)

    if not result:
        channel_id = None
    else:
        channel_id = result[0]
    return channel_id


async def delete_member_channel_id(_channel_id):
    db = botutils.SQLite3Helper()
    sql = MEMBER_CHANNEL_DELETE_SQL
    val = (_channel_id,)
    db.execute(sql, val)


async def check_member_category(ctx):
    # Make sure member channel categories are all configured properly
    discord_member_category = await create_member_category(ctx)
    return discord_member_category


async def create_member_category(ctx):
    # Query db for member category name, check if they exist, and create them if not. Returns setting value
    setting_catagory_name = await botutils.get_server_setting(ctx.guild.id, MC_CAT_NAME_SETTING)
    if not setting_catagory_name:
        await ctx.send(f'No member category name defined. Please set this value with {COMMAND_PREFIX}mc-setcategory.')
        return None

    # Due to Discord's 50 channel limit per category, we need to separate members into multiple categories.
    catname_ai = setting_catagory_name + ' [A-I]'
    catname_jz = setting_catagory_name + ' [J-Z]'

    # check to see if the [A-I] category exists
    discord_category_ai = discord.utils.get(ctx.guild.categories, name=catname_ai)
    if not discord_category_ai:
        await ctx.send(f'Category not found, creating {catname_ai}')
        print(f'Category not found, creating {catname_ai}')
        discord_category_ai = await ctx.guild.create_category(catname_ai)
        botutils.debug('Setting _everyone')
    else:
        # await ctx.send(f'Category found: {discord_category_ai.name}')
        print(f'Category found: {discord_category_ai.name}')

    discord_category_jz = discord.utils.get(ctx.guild.categories, name=catname_jz)
    if not discord_category_jz:
        await ctx.send(f'Category not found, creating {catname_jz}')
        print(f'Category not found, creating {catname_jz}')
        discord_category_jz = await ctx.guild.create_category(catname_jz)
    else:
        await ctx.send(f'Category found: {discord_category_jz.name}')
        print(f'Category found: {discord_category_jz.name}')
    return setting_catagory_name


class MemberChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Determine the registered owner of a channel, or the registered channel for a member
    @commands.command(name='whois')
    async def whois(self, ctx, *, name_to_check=None):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}whois {name_to_check} called by {ctx.author.display_name}')

        # If the command is called without a name, we look for the owner of the current channel
        if not name_to_check:
            author_id, author_nick = await get_member_channel_owner(ctx.guild.id, ctx.channel.id)
            if author_id:
                await ctx.send(f"{ctx.channel.mention} is registered to {author_nick} ({author_id}).")
            else:
                await ctx.send(f"{ctx.channel.mention} is not registered.")

        # If the last argument is a tagged channel, look up the owner of that channel
        elif name_to_check.startswith('<#'):
            channel_id = name_to_check[2:-1]
            author_id, author_nick = await get_member_channel_owner(ctx.guild.id, channel_id)
            if author_id:
                await ctx.send(f"{name_to_check} is registered to {author_nick} ({author_id}).")
            else:
                await ctx.send(f"{name_to_check} is not registered.")

        # If the name to look up is a tagged user, check to see if that user has a registered channel
        elif name_to_check.startswith('<@'):
            print(f'name_to_check.startswith("<@")')
            user_id = name_to_check[3:-1]
            discord_user = await bobobot.fetch_user(int(user_id))
            channel_id = await get_member_channel_id(ctx.guild.id, str(discord_user))
            if channel_id:
                user_channel = bobobot.get_channel(channel_id)
                await ctx.send(f"{name_to_check} is registered to channel ({user_channel.mention}).")
            else:
                await ctx.send(f"{name_to_check} is not registered.")

        # WHOIS can only be passed a tagged member or channel, or run in a registered channel.
        else:
            await ctx.send(f"{COMMAND_PREFIX}whois can only take a tagged member or channel.")

    # Creates member channel categories on a new server
    @commands.command(name='mc-setup', hidden=True)
    async def mc_setup(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}mc-setup called by {ctx.author.display_name}')
        await check_member_category(ctx)

    # Set the base category name for member channel categories.
    @commands.command(name='mc-setcategory', hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def mc_setcategory(self, ctx, categoryname):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}mc-setcategory {categoryname} called by {ctx.author.display_name}')
        discord_guild_id = ctx.guild.id
        await botutils.set_server_setting(discord_guild_id, MC_CAT_NAME_SETTING, categoryname)

    # Create a member channel for the member calling the command
    @commands.command(name='requestchannel')
    async def requestchannel(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}requestchannel called by {ctx.author.display_name}')
        db = botutils.SQLite3Helper()
        request_safenick = safe_nick(ctx.author.display_name)
        member_channel_id = await get_member_channel_id(ctx.guild.id, str(ctx.author))

        # If we get a channel ID, we need to verify that the channel still exists
        if (member_channel_id is not None) and (member_channel_id > 100_000_000_000_000_000):
            discord_member_channel = discord.utils.get(ctx.guild.channels, id=member_channel_id)
            # If the channel ID stored in the db does not exist, remove it, then continue on to channel creation
            if not discord_member_channel:
                print(f'Channel ID {member_channel_id} stored in db does not exist; removing record.')
                await delete_member_channel_id(member_channel_id)
            # If we found a channel in the db and the channel exists, tag the owner in their channel
            else:
                print(f'Channel exists: {member_channel_id}')
                await discord_member_channel.send(f'Welcome back to your channel, ' + format(ctx.author.mention))
                return

        # Verified that member's channel is not stored in the db and does not exist. Create one now.
        mc_category = await check_member_category(ctx)

        # Because categories are limited to 50 channels, we need to break up the alphabet into multiple categories
        # In practice, I found there to be a heavy distribution of names in the first 9 letters of the alphabet,
        # as well as a heavy distribution in letters j/k. For my primary server, these letter distributions ended up
        # two relatively equal categories.
        # TODO: Add configuration settings for number of categories, and letter distribution in each category
        letters_ai = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        conditions_ai = [request_safenick.startswith(first_letter) for first_letter in letters_ai]
        if any(conditions_ai):
            mc_name = mc_category + ' [A-I]'
        else:
            mc_name = mc_category + ' [J-Z]'

        discord_member_category = discord.utils.get(ctx.guild.categories, name=mc_name)
        discord_member_channel = await ctx.guild.create_text_channel(request_safenick, category=discord_member_category)
        sql = MEMBER_CHANNEL_SET_SQL
        val = (ctx.guild.id, str(ctx.author), ctx.author.display_name, discord_member_channel.id)
        db.execute(sql, val)
        print(f'{db.rowcount} channel added.')
        await sort_cat(ctx, mc_name)
        await discord_member_channel.send(f'Welcome to your channel, ' + format(ctx.author.mention))

