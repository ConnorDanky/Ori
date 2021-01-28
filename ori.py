import discord
from discord.ext import commands

import util.io_util as io_util

#adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents = intents)


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
    # Do this or else commands won't work!
    await ori.process_commands(message)


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


#Starting support for the ability to change roles
@ori.command()
async def role(ctx, member: discord.Member):
    cool_red = ctx.guild.get_role(804232490158915624)

    await member.add_roles(cool_red)

    await ctx.send(member.mention + " is now cool red! ")


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
ori.run(auth['token'])
