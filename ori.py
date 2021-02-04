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


#Support for welcoming new members
#NEED TO ADD DM SUPPORT ON BOTH ENTERING AND LEAVING (HELP/LINK TO COME BACK)

@ori.event
async def on_member_join(member):
    #format username
    
    user = await formName(member)
   
    print(f'{user} has joined a server!') #prints to console a new member joined
    #channel info
    channel = discord.utils.get(member.guild.channels,name = "welcome-channel") #name is specific to whatever you want the welcome messages to appear in
    #create an embeded box to welcome the new member
    mBed = discord.Embed(
        colour = (discord.Colour.blue()),
        title = "Welcome Message",
        description = "Hello, " + f'{user}' + ". Welcome to ConnorDanky's Arena!"

    )
    #display our embeded box
    await channel.send(embed=mBed)

#Support for outgoing players
@ori.event
async def on_member_remove(member):
    #format username    
    user = await formName(member)   
    print(f'{user} has left a server!')#prints to console the player left
    #channel info
    channel = discord.utils.get(member.guild.channels, name = "welcome-channel")#name is whatever channel you want the message to appear in
    #Embeded Box for display
    mBed = discord.Embed(
        colour = (discord.Colour.dark_purple()),
        title = "Leaving Message",
        description = "You hate to see it, but " + f'{user}' + " had to go."
    )
    #display for the embeded box
    await channel.send(embed = mBed)

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



#formatting username function
async def formName(member):
    user = str(member)
    userList = user.split('#')
    user = str(userList[0])
    return user


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
ori.run(auth['token'])
