import random
import json


import discord
from discord.ext import commands

import util.io_util as io_util
import util.string_util as string_util

# adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents=intents)


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

    await add_message(message.author)


# Support for welcoming new members
# NEED TO ADD DM SUPPORT ON BOTH ENTERING AND LEAVING (HELP/LINK TO COME BACK)

@ori.event
async def on_member_join(member):
    display_name = member.display_name

    print(f'{display_name} has joined a server!')  # prints to console a new member joined
    # channel info
    channel = discord.utils.get(member.guild.channels,
                                name="welcome-channel")  # name is specific to whatever you want the welcome messages
    # to appear in
    # create an embedded box to welcome the new member
    channel_embed = discord.Embed(
        color=(discord.Color.blue()),
        title="Welcome Message",
        description="Hello, " + f'{display_name}' + ". Welcome to ConnorDanky's Arena!"

    )
    user_embed = discord.Embed(
        color=(discord.Color.blue()),
        title="Hello! I am Ori!",
        description="I am your guide through the ConnorDanky_ Arena Discord Server. To see what I can do type !help. "
                    "\n In case you have to leave, here is the link so you can come back. ("
                    "https://discord.gg/cyTEjWkyMb) "
    )
    # display our embedded box
    await member.send(embed=user_embed)
    await channel.send(embed=channel_embed)


async def is_banned(member: discord.Member):
    bans = await member.guild.bans()
    return member in bans

# Easy Message Deleting

@ori.command(aliases = ['d'])
@commands.has_permissions(manage_messages = True)
async def delete(ctx,amount = 2):
    await ctx.channel.purge(limit = amount)


# Kicking Members

@ori.command(aliases = ['k'])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member : discord.Member,*,reason="No reason given!"):
    await member.send(f"You have been kicked from {member.guild.name}, because " + reason)
    await member.send("Come back if you can follow the rules: https://discord.gg/cyTEjWkyMb")
    await member.kick(reason=reason)


# Support for outgoing players
@ori.event
async def on_member_remove(member: discord.Member):
    member_id = member.id

    member_name = member.display_name
    print(f'{member_name} has left {member.guild.name}!')  # prints to console the player left

    # channel info
    channel = discord.utils.get(member.guild.channels,
                                name="welcome-channel")  # name is whatever channel you want the message to appear in
    # Embedded Box for display
    channel_embed = discord.Embed(
        colour=(discord.Colour.dark_purple()),
        title="Leaving Message",
        description="You hate to see it, but " + f'{member_name}' + " had to go."
    )
    user_embed = discord.Embed(
        colour=(discord.Colour.dark_purple()),
        title="Sorry to see you go :(",
        description="Unless you were banned, then good riddance! However if you are in good standing and would like "
                    "return, just click this link : http://discord.gg/" +
                    string_util.random_string(10, False, False) if is_banned(member) else "cyTEjWkyMb"  # Will give a
        # randomly generated link if banned
    )
    # display for the embedded box

    await channel.send(embed=channel_embed)

    left = ori.get_user(member_id)
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


# 'rs' command
@ori.command(name='rs')
async def random_screenshot(ctx):
    await ctx.send('https://prnt.sc/' + string_util.random_string(random.randrange(6, 7, 1), numbers=True))


# 'test' command
@ori.command()
async def test(ctx):
    # Check if its either Akoot_ or ConnorDanky_
    if ctx.author.id in [435993495627628545, 143202195502923776]:
        await ctx.send('https://discord.gg/' + string_util.random_string(10))


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

    if all(element == final[0] for element in final):
        await ctx.send(ctx.author.mention + " won! " + '<:opog:808534536270643270>')
    else:
        await ctx.send("Better Luck next time!")


# account systems - balance
@ori.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_inv_data()

    points_amt = users[str(user.id)]["points"]
    messages_amt = users[str(user.id)]["messages"]

    m_bed = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.red())
    m_bed.add_field(name = "Points", value = points_amt)
    m_bed.add_field(name = "Messages", value = messages_amt)

    await ctx.send(embed = m_bed)


# account systems - points(beg)
@ori.command()
async def work(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_inv_data()

    earnings = random.randrange(101)
    await ctx.send(f"You worked all day and got {earnings} points!!")   
    
    
    users[str(user.id)]["points"] += earnings

    with open("account.json","w") as f:
        json.dump(users,f)


# account systems - opening account
async def open_account(user):
    
    users = await get_inv_data()

    # checks if an account exsists
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["points"] = 0
        users[str(user.id)]["messages"] = 0

    with open("account.json","w") as f:
        json.dump(users,f)
    return True

# account systems - inventory data
async def get_inv_data():
    with open("account.json","r") as f:
        users = json.load(f)

    return users

# account systems - message counter
async def add_message(caller):
    await open_account(caller)
    user = caller
    users = await get_inv_data()    
    
    users[str(user.id)]["messages"] += 1

    with open("account.json","w") as f:
        json.dump(users,f)

# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
ori.run(auth['token'])
