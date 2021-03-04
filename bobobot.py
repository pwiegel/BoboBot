# Bobobot.py
# discord.py 1.3.3

from bot import bobobot
from botconfig import COMMAND_PREFIX, DISCORD_TOKEN
from botutils import timenow

import discord
from discord.ext import commands
from datetime import datetime

COG_IMGUR = "cogs.imgurcog"
COG_PURGE = "cogs.purgecog"
COG_TIMEBOMB = "cogs.timebombcog"
COG_XP5E = "cogs.xp5ecog"
COG_SPOILER = "cogs.spoilercog"
COG_MEMBERCHANNEL = "cogs.memberchannelcog"
COG_STATS = "cogs.statscog"

bobobot.remove_command('help')


@bobobot.event
async def on_ready():
    print(f'{timenow()} - {bobobot.user.name} has connected to Discord!')


@bobobot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.BotMissingPermissions):
        print('403 Forbidden (error code: 50013): Bot is missing permissions for this action.')
    else:
        print(error)


@bobobot.command(name='help')
async def bot_help(ctx):
    print(f'{timenow()} ***** Bot Command: {COMMAND_PREFIX}help called by {ctx.author.display_name}')
    # TODO: write xp help embed
    xp_help_embed = discord.Embed(title="Bobo Bot Help", timestamp=datetime.now(), color=discord.Color.blue())
    # xp_help_embed.add_field(name=f"{COMMAND_PREFIX}Member Channels", inline=True)
    xp_help_embed.add_field(name=f"Pic commands",
                            value=f"This group of commands responds with a random picture from the relevant imgur album."
                                  f"```"
                                  f"{COMMAND_PREFIX}meetpic   : Posts a random pic from the 18nUp group meetups\n\n"
                                  f"{COMMAND_PREFIX}campimgur : Posts a random pic from the bot author's Camp Imgur album.\n\n"
                                  f"{COMMAND_PREFIX}bobopic   : Posts a random pic of Bobo, the bot's namesake.\n\n"
                                  f"```", inline=False)
    xp_help_embed.add_field(name=f"Timebomb Commands",
                            value=f"This group of commands enables expiring messages and photos."
                                  f"```"
                                  f"{COMMAND_PREFIX}timebomb <time> : message is deleted after <time>. Time can be in (m)inutes, (h)ours, or (days). Ex: 30m, 2h, 7d\n\n"
                                  f"{COMMAND_PREFIX}explodemine     : Immediately deletes all of your timebombs, regardless of time left.\n\n"
                                  f"```", inline=False)
    xp_help_embed.add_field(name=f"Spoiler Commands",
                            value=f"This group of commands helps post spoilered photos and links."
                                  f"```"
                                  f"{COMMAND_PREFIX}spoiler <message> : Reposts the text after the command as a spoiler, then deletes the original message\n\n"
                                  f"{COMMAND_PREFIX}spoiler           : Mobile: Reposts all attached photos as spoiled photos and deletes the original message.\n\n"
                                  f"{COMMAND_PREFIX}spoiler           : Desktop: Just check 'Mark as spoiler' on the image upload dialogue box.\n\n"
                                  f"```", inline=False)
    xp_help_embed.add_field(name=f"Member Channels",
                            value=f"This group of commands enables server members to request their own channel."
                                  f"```"
                                  f"{COMMAND_PREFIX}requestchannel : Creates a channel for you. If the command is successful you will be tagged in your new channel.\n\n"
                                  f"{COMMAND_PREFIX}whois <target> : Query a member's channel or the owner of a member channel. Target can be the text or tag name of a member or channel.\n\n"
                                  f"==========\n"
                                  f"Admin Only Commands:\n\n"
                                  f"{COMMAND_PREFIX}mc-setcategory  : Sets the base name of the Member Category. This will be split based on alphabet as appropriate.\n\n"
                                  f"{COMMAND_PREFIX}mc-setup        : Creates the Member Channel categories based on the mc-setcategory value.\n\n"
                                  f"```", inline=False)
    xp_help_embed.add_field(name=f"Sherlock Hulmes 5e XP System Tracker",
                            value=f"This group of commands allows a 5e party to track XP on a per-session basis using Sherlock Hulmes 5e XP system.\n"
                                  f"Reference: https://i.imgur.com/vvWnSO5.png\n"
                                  f"```"
                                  f"{COMMAND_PREFIX}xphelp : Dedicated help command for this XP tracker.\n\n"
                                  f"```", inline=False)

    await ctx.send(embed=xp_help_embed)


bobobot.load_extension(COG_PURGE)
bobobot.load_extension(COG_TIMEBOMB)
bobobot.load_extension(COG_SPOILER)
bobobot.load_extension(COG_MEMBERCHANNEL)
bobobot.load_extension(COG_IMGUR)
bobobot.load_extension(COG_XP5E)
bobobot.load_extension(COG_STATS)
bobobot.run(DISCORD_TOKEN)
