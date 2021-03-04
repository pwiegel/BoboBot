# statscog.py
# Data stored:
# Permissions needed: READ_MESSAGES, SEND_MESSAGES

import botutils
from botconfig import COMMAND_PREFIX
from discord.ext import commands


def setup(bot):
    bot.add_cog(StatsCog(bot))


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='membercount')
    async def membercount(self, ctx):
        print(f'{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}membercount called by {ctx.author.display_name}')
        await ctx.send(f"{ctx.guild.name} has {ctx.guild.member_count} members")


