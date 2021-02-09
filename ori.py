import random

import discord
from discord.ext import commands

import util.io_util as io_util

# adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents=intents)


# Get all roles from roles.json
def get_roles(guild: discord.Guild):
    roles = {}
    for guild_role in guild.roles:
        roles[guild_role.name] = guild_role.id
    return roles


# Get a role
def get_role(guild: discord.Guild, name: str):
    return guild.get_role(get_roles(guild)[name])


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


# Support for welcoming new members
# NEED TO ADD DM SUPPORT ON BOTH ENTERING AND LEAVING (HELP/LINK TO COME BACK)

@ori.event
async def on_member_join(member):
    # format username

    user = await form_name(member)

    print(f'{user} has joined a server!')  # prints to console a new member joined
    # channel info
    channel = discord.utils.get(member.guild.channels,
                                name="welcome-channel")  # name is specific to whatever you want the welcome messages
    # to appear in
    # create an embedded box to welcome the new member
    channel_embed = discord.Embed(
        colour=(discord.Colour.blue()),
        title="Welcome Message",
        description="Hello, " + f'{user}' + ". Welcome to ConnorDanky's Arena!"

    )
    user_embed = discord.Embed(
        colour=(discord.Colour.blue()),
        title="Hello! I am Ori!",
        description="I am your guide through the ConnorDanky_ Arena Discord Server. To see what I can do type !help. "
                    "\n In case you have to leave, here is the link so you can come back. ("
                    "http://discord.gg/FKGBjAdQPT) "
    )
    # display our embedded box
    await member.send(embed=user_embed)
    await channel.send(embed=channel_embed)


# Support for outgoing players
@ori.event
async def on_member_remove(member):
    # format username
    id_ = member.id

    user = await form_name(member)
    print(f'{user} has left a server!')  # prints to console the player left
    # channel info
    channel = discord.utils.get(member.guild.channels,
                                name="welcome-channel")  # name is whatever channel you want the message to appear in
    # Embedded Box for display
    channel_embed = discord.Embed(
        colour=(discord.Colour.dark_purple()),
        title="Leaving Message",
        description="You hate to see it, but " + f'{user}' + " had to go."
    )
    user_embed = discord.Embed(
        colour=(discord.Colour.dark_purple()),
        title="Sorry to see you go :(",
        description="Unless you were banned, then good riddance! However if you are in good standing and would like "
                    "return, just click this link : http://discord.gg/FKGBjAdQPT "
    )
    # display for the embedded box

    await channel.send(embed=channel_embed)

    left = ori.get_user(id_)
    await left.send(embed=user_embed)


# 'spaghetti' command
@ori.command()
async def spaghetti(ctx):
    await ctx.send('and meatballs')


# 'ud' command
@ori.command()
async def ud(ctx, *args):
    await ctx.send('https://www.urbandictionary.com/define.php?term=' + '+'.join(args))


# 'define' command
@ori.command()
async def define(ctx, *args):
    await ctx.send('https://www.merriam-webster.com/dictionary/' + '%20'.join(args))


# Slot bars
slot_bars = [':ringed_planet:', ':mushroom:', ':rainbow:', '<:opog:808534536270643270>', ':gem:']


# Slot Machine - Purely for fun. No money or anything
@ori.command()
async def slots(ctx):
    final = []
    for i in range(3):
        a = random.choice(slot_bars)
        final.append(a)
    await ctx.send("".join(final))

    if final[0] == final[1] and final[0] == final[2] and final[1] == final[2]:
        await ctx.send(ctx.author.mention + " won! " + '<:opog:808534536270643270>')
    else:
        await ctx.send("Better Luck next time!")


# formatting username function
async def form_name(member):
    user = str(member)
    user_list = user.split('#')
    user = str(user_list[0])
    return user


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
ori.run(auth['token'])
