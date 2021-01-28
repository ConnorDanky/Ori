from discord.ext import commands

import util.io_util as io_util

# Create Ori instance
ori = commands.Bot(command_prefix='!')


# on_ready event
@ori.event
async def on_ready():
    print('Logged on as', ori.user)


# on_message event
@ori.event
async def on_message(message):
    # don't respond to ourselves
    if message.author == ori.user:
        return  # Do nothing


# 'spaghetti' command
# TODO: figure out how commands work cause this ain't working!
@ori.command()
async def spaghetti(ctx):
    await ctx.send('and meatballs')


# 'ud' command
@ori.command()
async def ud(ctx, *args):
    await ctx.send('https://www.urbandictionary.com/define.php?term=', '+'.join(args), sep='')


# 'define' command
@ori.command()
async def define(ctx, *args):
    await ctx.send('https://www.merriam-webster.com/dictionary/', '+'.join(args), sep='%20')


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
ori.run(auth['token'])
