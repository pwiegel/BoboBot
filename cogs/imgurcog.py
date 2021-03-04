# imgurcog.py
# Data stored: Imgur album IDs
# Permissions needed: READ_MESSAGES, SEND_MESSAGES

import imgurpython
import random
from imgurpython.helpers.error import ImgurClientError
from discord.ext import commands
from botconfig import COMMAND_PREFIX, IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET
from botutils import timenow


def setup(bot):
    bot.add_cog(ImgurCog(bot))


async def get_imgurpic(imgur_album_id):
    """ Returns the URL of a random image from a given Imgur album

    :parameter
    imgur_album_id : The ID string for an Imgur album. (Ex: '8zcyw')

    :return
    String containing an image URL
    """
    imgur_client = imgurpython.ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
    image_url_list = []

    # Get a list of image objects from the album
    try:
        imgur_album_images = imgur_client.get_album_images(imgur_album_id)
    except ImgurClientError:
        print(str(ImgurClientError))
        return 'The Imgur API returned an error. Please try again or wait a few minutes if this error happens again.'

    # extract a list of image links from the list of image objects, then return a random image link
    for image_url in imgur_album_images:
        image_url_list.append(image_url.link)
    return random.choice(image_url_list)


class ImgurCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # To create new commands, simply copy one of the below commands, then change the command and function names,
    # the command name in the print statement, and then change the imgur album ID.
    @commands.command(name='bobo')
    async def bobo(self, ctx):
        print(f'{timenow()} ***** Bot Command: {COMMAND_PREFIX}bobo called by {ctx.author.display_name}')
        response = await get_imgurpic('8zcyw')
        await ctx.send(response)

    @commands.command(name='bunbun')
    async def bunbun(self, ctx):
        print(f'{timenow()} ***** Bot Command: {COMMAND_PREFIX}bunbun called by {ctx.author.display_name}')
        response = await get_imgurpic('R6bJju4')
        await ctx.send(response)

