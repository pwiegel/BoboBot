# spoilercog.py
# Permissions needed: READ_MESSAGES, SEND_MESSAGES, EMBED_LINKS, ATTACH_FILES, MANAGE_MESSAGES

import botutils
from botconfig import COMMAND_PREFIX
from discord.ext import commands
from discord import File
from aiohttp import ClientSession
from io import BytesIO


def setup(bot):
    bot.add_cog(SpoilerCog(bot))


class SpoilerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='spoiler', aliases=['s'])
    async def spoiler(self, ctx, *, message=None):
        print(f"{botutils.timenow()} ***** Bot Command: {COMMAND_PREFIX}spoiler called by {ctx.author.display_name}")
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'}

        if message:
            await ctx.send(f'Spoilered text from {ctx.author.display_name}: ||{message}||')

        for attachment in ctx.message.attachments:
            session = ClientSession()
            async with session.get(attachment.url, headers=header) as response:
                file = BytesIO(await response.read())
            sp_file = File(file, filename=f'SPOILER_{attachment.filename}', spoiler=True)
            await ctx.send(f"Spoilered image from {ctx.author.display_name}:", file=sp_file)
            await session.close()

        await ctx.message.delete()
