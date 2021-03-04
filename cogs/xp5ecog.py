# xp5ecog.py
# Data stored: Guild ID, Channel ID, submitted D&D info
# Permissions needed: READ_MESSAGES, SEND_MESSAGES, EMBED_LINKS

import botutils
from botconfig import COMMAND_PREFIX
from discord.ext import commands
from datetime import datetime
import discord

XP_5E_LEVEL_2 = 300
XP_5E_LEVEL_3 = 900
XP_5E_LEVEL_4 = 2700
XP_5E_LEVEL_5 = 6500
XP_5E_LEVEL_6 = 14000
XP_5E_LEVEL_7 = 23000
XP_5E_LEVEL_8 = 34000
XP_5E_LEVEL_9 = 48000
XP_5E_LEVEL_10 = 64000
XP_5E_LEVEL_11 = 85000
XP_5E_LEVEL_12 = 100000
XP_5E_LEVEL_13 = 120000
XP_5E_LEVEL_14 = 140000
XP_5E_LEVEL_15 = 165000
XP_5E_LEVEL_16 = 195000
XP_5E_LEVEL_17 = 225000
XP_5E_LEVEL_18 = 265000
XP_5E_LEVEL_19 = 305000
XP_5E_LEVEL_20 = 355000


CREATE_TABLE_PARTY_XP = '''
CREATE TABLE IF NOT EXISTS Party_XP (
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Guild_ID INTEGER NOT NULL,
    Channel_ID INTEGER NOT NULL,
    Total_XP INTEGER NOT NULL,
    CONSTRAINT Party_XP_UN UNIQUE (Guild_ID,Channel_ID)
);

'''

CREATE_TABLE_PARTY_XP_SESSION = '''
CREATE TABLE IF NOT EXISTS Party_XP_Session (
    ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Guild_ID INTEGER NOT NULL,
    Channel_ID INTEGER NOT NULL,
    Session_Date TEXT NOT NULL,
    Current_XP INTEGER NOT NULL,
    Session_XP INTEGER NOT NULL,
    Base_Session_XP INTEGER NOT NULL,
    Encounter_XP INTEGER NOT NULL,
    STG_XP INTEGER NOT NULL,
    Attuned_xp INTEGER NOT NULL,
    Trait_XP INTEGER NOT NULL,
    Relationship_XP INTEGER NOT NULL,
    Lore_XP INTEGER NOT NULL,
    Problem_XP INTEGER NOT NULL,
    Journey_XP INTEGER NOT NULL,
    Failed_XP INTEGER NOT NULL,
    Impact_XP INTEGER NOT NULL,
    CONSTRAINT Party_XP_Session_UN UNIQUE (Guild_ID,Channel_ID,Session_Date)
)
'''

# Create the Party_XP and Party_XP_Session tables if they do not exist
botutils.initialize_table(CREATE_TABLE_PARTY_XP)
botutils.initialize_table(CREATE_TABLE_PARTY_XP_SESSION)


def setup(bot):
    bot.add_cog(XP5eCog(bot))


def get_party_level(party_xp):
    """ Take in the current party XP, then calculate the party's level and the amount of experience until next level.

    :param party_xp: Current party XP
    :return: Current Level, XP to next level
    """
    if party_xp < XP_5E_LEVEL_2:
        next_level = XP_5E_LEVEL_2 - party_xp
        return 1, next_level
    elif XP_5E_LEVEL_2 <= party_xp < XP_5E_LEVEL_3:
        next_level = XP_5E_LEVEL_3 - party_xp
        return 2, next_level
    elif XP_5E_LEVEL_3 <= party_xp < XP_5E_LEVEL_4:
        next_level = XP_5E_LEVEL_4 - party_xp
        return 3, next_level
    elif XP_5E_LEVEL_4 <= party_xp < XP_5E_LEVEL_5:
        next_level = XP_5E_LEVEL_5 - party_xp
        return 4, next_level
    elif XP_5E_LEVEL_5 <= party_xp < XP_5E_LEVEL_6:
        next_level = XP_5E_LEVEL_6 - party_xp
        return 5, next_level
    elif XP_5E_LEVEL_6 <= party_xp < XP_5E_LEVEL_7:
        next_level = XP_5E_LEVEL_7 - party_xp
        return 6, next_level
    elif XP_5E_LEVEL_7 <= party_xp < XP_5E_LEVEL_8:
        next_level = XP_5E_LEVEL_8 - party_xp
        return 7, next_level
    elif XP_5E_LEVEL_8 <= party_xp < XP_5E_LEVEL_9:
        next_level = XP_5E_LEVEL_9 - party_xp
        return 8, next_level
    elif XP_5E_LEVEL_9 <= party_xp < XP_5E_LEVEL_10:
        next_level = XP_5E_LEVEL_10 - party_xp
        return 9, next_level
    elif XP_5E_LEVEL_10 <= party_xp < XP_5E_LEVEL_11:
        next_level = XP_5E_LEVEL_11 - party_xp
        return 10, next_level
    elif XP_5E_LEVEL_11 <= party_xp < XP_5E_LEVEL_12:
        next_level = XP_5E_LEVEL_12 - party_xp
        return 11, next_level
    elif XP_5E_LEVEL_12 <= party_xp < XP_5E_LEVEL_13:
        next_level = XP_5E_LEVEL_13 - party_xp
        return 12, next_level
    elif XP_5E_LEVEL_13 <= party_xp < XP_5E_LEVEL_14:
        next_level = XP_5E_LEVEL_14 - party_xp
        return 13, next_level
    elif XP_5E_LEVEL_14 <= party_xp < XP_5E_LEVEL_15:
        next_level = XP_5E_LEVEL_15 - party_xp
        return 14, next_level
    elif XP_5E_LEVEL_15 <= party_xp < XP_5E_LEVEL_16:
        next_level = XP_5E_LEVEL_16 - party_xp
        return 15, next_level
    elif XP_5E_LEVEL_16 <= party_xp < XP_5E_LEVEL_17:
        next_level = XP_5E_LEVEL_17 - party_xp
        return 16, next_level
    elif XP_5E_LEVEL_17 <= party_xp < XP_5E_LEVEL_18:
        next_level = XP_5E_LEVEL_18 - party_xp
        return 17, next_level
    elif XP_5E_LEVEL_18 <= party_xp < XP_5E_LEVEL_19:
        next_level = XP_5E_LEVEL_19 - party_xp
        return 18, next_level
    elif XP_5E_LEVEL_19 <= party_xp < XP_5E_LEVEL_20:
        next_level = XP_5E_LEVEL_20 - party_xp
        return 19, next_level
    elif party_xp >= XP_5E_LEVEL_20:
        return 20, 0


class XPSession:
    """ An object representing a play session of D&D

    """
    GET_PARTY_XP_SQL = "SELECT Total_XP FROM Party_XP WHERE Guild_ID = ? AND Channel_ID = ?"
    SET_CHANNEL_XP_SQL = "INSERT INTO Party_XP (Guild_ID, Channel_ID, Total_XP) VALUES (?, ?, ?)"
    SET_PARTY_XP_SQL = "UPDATE Party_XP SET Total_XP = ? WHERE Guild_ID = ? AND Channel_ID = ?"
    GET_SESSION_DETAIL_SQL = "SELECT * FROM Party_XP_Session WHERE Guild_ID=? AND Channel_ID=? AND Session_Date=?"
    SAVE_SESSION_SQL = "INSERT INTO Party_XP_Session (" \
                       "Guild_ID, " \
                       "Channel_ID, " \
                       "Session_Date, " \
                       "Current_XP, " \
                       "Session_XP, " \
                       "Base_Session_XP, " \
                       "Encounter_XP, " \
                       "STG_XP, " \
                       "Attuned_XP, " \
                       "Trait_XP, " \
                       "Relationship_XP, " \
                       "Lore_XP, " \
                       "Problem_XP, " \
                       "Journey_XP, " \
                       "Failed_XP, " \
                       "Impact_XP" \
                       ") VALUES (" \
                       "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?" \
                       ");"

    def __init__(self, ctx=None, session_id=None):
        self.session_id = session_id
        self.ctx = ctx
        self.guild_id = 0
        self.channel_id = 0
        self.level = 0
        self.next_level = 0
        self.new_level = 0
        self.new_next_level = 0
        self.date = ''
        self.party_current_xp = 0
        self.session_total_xp = 0
        self.party_new_total_xp = 0
        self.base_xp = 0
        self.encounter_difficulty = ''
        self.encounter_xp = 0
        self.stg_xp = 0
        self.attuned_xp = 0
        self.trait_xp = 0
        self.relationship_xp = 0
        self.lore_xp = 0
        self.problem_xp = 0
        self.journey_xp = 0
        self.failed_xp = 0
        self.impact_xp = 0
        self.embed_title = ''
        self.embed_level = ''
        self.embed_detail = ''
        self.result = None

        if self.ctx is not None:
            self.guild_id = self.ctx.guild.id
            self.channel_id = self.ctx.channel.id

        self.load_xp()

        if self.session_id is not None:
            self.load_session()

    def set_xp_channel(self, starting_xp: int = 0):
        """ If the current channel does not exist in the database, create it to begin tracking XP in this channel.

        :parameter
        starting_xp : int
        This is the XP value at which to begin tracking the party's experience in the event of adding tracking to an
        existing game. For a new game in which the party has not yet played a session, the default value of 0 is used.

        :return
        There is no return value.
        """
        db = botutils.SQLite3Helper()
        sql = self.SET_CHANNEL_XP_SQL
        val = (self.ctx.guild.id, self.ctx.channel.id, starting_xp)
        result = db.execute(sql, val)
        self.load_xp()
        return result

    def load_xp(self):
        """ Retrieve the current party XP value for the current channel."""
        sql = self.GET_PARTY_XP_SQL
        val = (self.ctx.guild.id, self.ctx.channel.id)
        db = botutils.SQLite3Helper()
        result = db.fetchone(sql, val)
        if result:
            self.party_current_xp = result[0]
            self.level, self.next_level = get_party_level(self.party_current_xp)
        else:
            self.party_current_xp = None
            print('XPSession.load_XP() returned 0 results')
        return result

    def save_xp(self):
        sql = self.SET_PARTY_XP_SQL
        val = (self.party_new_total_xp, self.ctx.guild.id, self.ctx.channel.id)
        db = botutils.SQLite3Helper()
        result = db.execute(sql, val)
        return result

    def calc_session_xp(self):
        self.session_total_xp = self.base_xp + \
                                self.encounter_xp + \
                                self.stg_xp + \
                                self.attuned_xp + \
                                self.trait_xp + \
                                self.relationship_xp + \
                                self.lore_xp + \
                                self.problem_xp + \
                                self.journey_xp + \
                                self.failed_xp + \
                                self.impact_xp
        self.party_new_total_xp = self.party_current_xp + self.session_total_xp
        self.new_level, self.new_next_level = get_party_level(self.party_new_total_xp)

    def calculate_xp(self):
        if self.party_current_xp is None:
            raise ValueError('Pre_Session_XP has not been defined. Call .load_session() or .load_xp().')
        else:
            self.level = get_party_level(self.party_current_xp)
            self.level, self.next_level = get_party_level(self.party_current_xp)
        self.party_new_total_xp = self.party_current_xp + self.session_total_xp
        self.new_level, self.new_next_level = get_party_level(self.party_new_total_xp)

    def load_session(self):
        self.guild_id = self.ctx.guild.id
        self.channel_id = self.ctx.channel.id
        sql = self.GET_SESSION_DETAIL_SQL
        val = (self.guild_id, self.channel_id, self.session_id)
        db = botutils.SQLite3Helper()
        result_set = db.fetch(sql, val)
        if len(result_set) == 0:
            self.session_id = -1
            return
        for result in result_set:
            self.date = result[3]
            self.party_current_xp = result[4]
            self.session_total_xp = result[5]
            self.base_xp = result[6]
            self.encounter_xp = result[7]
            self.stg_xp = result[8]
            self.attuned_xp = result[9]
            self.trait_xp = result[10]
            self.relationship_xp = result[11]
            self.lore_xp = result[12]
            self.problem_xp = result[13]
            self.journey_xp = result[14]
            self.failed_xp = result[15]
            self.impact_xp = result[16]

        self.calculate_xp()
        self.generate_session_embed_strings()

    async def save_session(self):
        sql = self.SAVE_SESSION_SQL
        val = (
            self.guild_id,
            self.channel_id,
            self.date,
            self.party_current_xp,
            self.session_total_xp,
            self.base_xp,
            self.encounter_xp,
            self.stg_xp,
            self.attuned_xp,
            self.trait_xp,
            self.relationship_xp,
            self.lore_xp,
            self.problem_xp,
            self.journey_xp,
            self.failed_xp,
            self.impact_xp
        )
        db = botutils.SQLite3Helper()
        result = db.execute(sql, val)
        return result

    def get_encounter_xp(self):
        if self.encounter_difficulty.lower() == 'easy':
            self.encounter_xp = self.level * 50
        elif self.encounter_difficulty.lower() == 'medium':
            self.encounter_xp = self.level * 100
        elif self.encounter_difficulty.lower() == 'hard':
            self.encounter_xp = self.level * 150
        elif self.encounter_difficulty.lower() == 'deadly':
            self.encounter_xp = self.level * 200
        else:
            self.encounter_xp = None

    def generate_session_embed_strings(self):
        self.embed_title = f"{self.date}\nSession XP: *{self.session_total_xp:,}*\n"
        if self.new_level == 20:
            self.embed_level = f"Level: *{self.new_level}*\n" \
                               f"Total XP: *{self.party_new_total_xp:,}*\n"
        elif self.session_total_xp >= self.next_level:
            self.embed_level = f"***CONGRATULATIONS!*** \n" \
                               f"Your party advanced to level: *{self.new_level}*\n\n" \
                               f"Starting Level: *{self.level:,}*\n" \
                               f"Starting XP: *{self.party_current_xp:,}*\n" \
                               f"Session XP: *{self.session_total_xp:,}*\n" \
                               f"New Total XP: *{self.party_new_total_xp:,}*\n" \
                               f"Next Level: *{self.new_next_level:,}*"
        else:
            self.embed_level = f"Level: *{self.level}*\n" \
                               f"Starting XP: *{self.party_current_xp:,}*\n" \
                               f"Session XP: *{self.session_total_xp:,}*\n" \
                               f"New Total XP: *{self.party_new_total_xp:,}*\n" \
                               f"Next Level: *{self.new_next_level:,}*"
        self.embed_detail = f"```" \
                            f"Base Session XP: {self.base_xp}\n" \
                            f"Encounter XP: {self.encounter_xp}\n" \
                            f"Short Term Goal: {self.stg_xp}\n" \
                            f"Attuned Magic Item: {self.attuned_xp}\n" \
                            f"Bond/Ideal/Flaw: {self.trait_xp}\n" \
                            f"Relationship Development: {self.relationship_xp}\n" \
                            f"New Lore: {self.lore_xp}\n" \
                            f"Skill/Spell Problem Solving: {self.problem_xp}\n" \
                            f"Perilous Journey: {self.journey_xp}\n" \
                            f"Failed Roll: {self.failed_xp}\n" \
                            f"Impactful Actions: {self.impact_xp}\n" \
                            f"```"


class XP5eCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='trackxp')
    async def trackxp(self, ctx, starting_xp=0):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}trackxp called by {ctx.author.display_name}')
        session = XPSession(ctx)
        if session.party_current_xp is not None:
            await ctx.send(f'{ctx.channel.mention} already tracked with {session.party_current_xp} XP!')
            return

        session.set_xp_channel(starting_xp)
        if session.party_current_xp is not None:
            await ctx.send(f'Now tracking {ctx.channel.mention}! Use {COMMAND_PREFIX}addsession to add sessions!')
        else:
            await ctx.send('OH NOES! Something went wrong! EVERYBODY PANIC!!!! D:')

    @commands.command(name='showxp')
    async def showxp(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}showxp called by {ctx.author.display_name}')

        session = XPSession(ctx)
        if session.party_current_xp is None:
            await ctx.send(f'{ctx.channel.mention} is not being tracked. Use {COMMAND_PREFIX}trackxp to begin tracking party XP!')
            return

        if session.level == 20:
            await ctx.send(f'Your party is level {session.level} with {session.party_current_xp:,} XP. Your party is max level. *golf clap*')
        else:
            await ctx.send(f'Your party is level {session.level} with {session.party_current_xp:,} XP. You have {session.next_level:,} XP until next level!')

    @commands.command(name='listsession', aliases=['ls'])
    async def listsession(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}listsession called by {ctx.author.display_name}')
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id
        db = botutils.SQLite3Helper()
        GET_SESSION_LIST_SQL = "SELECT session_date, current_xp, session_xp FROM party_xp_session WHERE guild_id=? AND channel_id=?"
        sql = GET_SESSION_LIST_SQL
        val = (guild_id, channel_id)
        resultset = db.fetch(sql, val)
        session_list_embed_string = ''
        if len(resultset) == 0:
            await ctx.send("No sessions found.")
            return
        else:
            for result in resultset:
                session_list_embed_string = session_list_embed_string + f"{result[0]} - Starting XP: {result[1]:,}, Session XP: {result[2]:,}\n"

        xp_list_session_embed = discord.Embed(title="Sessions", timestamp=datetime.now(), color=discord.Color.blue())
        xp_list_session_embed.add_field(name=f"Sessions", value=f"```{session_list_embed_string}```")

        await ctx.send(embed=xp_list_session_embed)

    @commands.command(name='showsession', aliases=['ss'])
    async def showsession(self, ctx, session_id=None):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}showsession {session_id} called by {ctx.author.display_name}')
        if not session_id:
            await ctx.send(f"No session specified. Please use session date in the form: YYYY-MM-DD.")
            return

        session = XPSession(ctx, session_id)
        ss_embed = discord.Embed(title=session.embed_title, timestamp=datetime.now(), color=discord.Color.blue())
        ss_embed.add_field(name="__Level & XP__", value=session.embed_level, inline=False)
        ss_embed.add_field(name="__Details__", value=session.embed_detail, inline=False)

        await ctx.send(embed=ss_embed)

    @commands.command(name='addsession', aliases=['as'])
    async def addsession(self, ctx, session_date, *session_args):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}addsession {session_date} {session_args} called by {ctx.author.display_name}')
        session_args = [arg.lower() for arg in session_args] 
        valid_args = ['easy', 'medium', 'hard', 'deadly', 'stg', 'attuned', 'trait', 'relationship', 'lore', 'problem',
                      'journey', 'failed', 'impact']
        if session_args is not None:
            for arg in session_args:
                if arg not in valid_args:
                    await ctx.send(f'{arg} is not a valid value.')
                    return

        session = XPSession(ctx)
        session.date = session_date
        session.load_xp()

        # Calculate session XP
        session.base_xp = session.level * 100
        encounter_difficulties = {'easy', 'medium', 'hard', 'deadly'}
        for difficulty in encounter_difficulties:
            if difficulty in session_args:
                session.encounter_difficulty = difficulty
                session_args.remove(difficulty)
                session.get_encounter_xp()

        if 'stg' in session_args:
            session.stg_xp = session.level * 200
        if 'attuned' in session_args:
            session.attuned_xp = session.level * 25
        if 'trait' in session_args:
            session.trait_xp = session.level * 25
        if 'relationship' in session_args:
            session.relationship_xp = session.level * 25
        if 'lore' in session_args:
            session.lore_xp = session.level * 25
        if 'problem' in session_args:
            session.problem_xp = session.level * 25
        if 'journey' in session_args:
            session.journey_xp = session.level * 25
        if 'failed' in session_args:
            session.failed_xp = session.level * 25
        if 'impact' in session_args:
            session.impact_xp = session.level * 25

        session.calc_session_xp()
        save_session_result = await session.save_session()
        if save_session_result is None:
            await ctx.send(f'Error saving session {session.date}: Server: {ctx.guild.id}, Channel: {ctx.channel.id}')
            return

        save_xp_result = session.save_xp()
        if save_xp_result is None:
            await ctx.send(f'Error updating party XP: Server: {ctx.guild.id}, Channel: {ctx.channel.id}, New XP value: {session.party_new_total_xp:,}')
            return

        session.generate_session_embed_strings()

        session_xp_embed = discord.Embed(title=session.embed_title, timestamp=datetime.now(),
                                         color=discord.Color.blue())
        session_xp_embed.add_field(name="__Updated Level & XP__",
                                   value=session.embed_level)
        session_xp_embed.add_field(name=f"__Details__",
                                   value=session.embed_detail, inline=False)
        await ctx.send(embed=session_xp_embed)

    @commands.command(name='xphelp')
    async def xphelp(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}xphelp called by {ctx.author.display_name}')

        xp_help_embed = discord.Embed(title="XP System Help", timestamp=datetime.now(), color=discord.Color.blue())
        xp_help_embed.add_field(name=f"{COMMAND_PREFIX}trackxp",
                                value=f"Begin tracking party XP. Party XP is tied to a single channel.")
        xp_help_embed.add_field(name=f"{COMMAND_PREFIX}showxp", value=f"Show current XP for this party.")
        xp_help_embed.add_field(name=f"{COMMAND_PREFIX}setxp <xp>",
                                value=f"DM Only: Set current party XP to an explicit value.")
        # xp_help_embed.add_field(name=f"{COMMAND_PREFIX}addsession <rule>=<setting>", value=f"Calculate session XP and report new party XP/level/XP to next level.")
        xp_help_embed.add_field(name=f"{COMMAND_PREFIX}addsession <YYYY-MM-DD> <keyword1> <keyword2> <keyword...>",
                                value=f"Simply include the keywords that the party is receiving XP for this session."
                                      f"```"
                                      f"[Easy|Medium|Hard|Deadly] : Encounter Difficulty (1 per difficulty)\n"
                                      f"stg                       : Short Term Goal\n"
                                      f"attuned                   : Attuned Magic Item\n"
                                      f"trait                     : Bond/Ideal/Flaw\n"
                                      f"relationship              : Relationship Development\n"
                                      f"lore                      : New Lore\n"
                                      f"problem                   : Skill/Spell Problem Solving\n"
                                      f"journey                   : Perilous Journey\n"
                                      f"failed                    : Failed Roll\n"
                                      f"impact                    : Impactful Actions\n\n"
                                      f"Example:\n"
                                      f"During the session, the party survived a Hard encounter, attuned a new magic item, discovered some lore, and failed a significant roll.\n"
                                      f"{COMMAND_PREFIX}addsession Hard attuned lore failed\n"
                                      f"```", inline=False)

        await ctx.send(embed=xp_help_embed)

