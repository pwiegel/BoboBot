import discord.ext

from botconfig import COMMAND_PREFIX

bobobot = discord.ext.commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True)

