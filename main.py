import json

from discord.ext import commands

# Create Ori instance
ori = commands.Bot(command_prefix='>')


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

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')


# Test '>spaghetti' command
# TODO: figure out how commands work cause this ain't working!
@ori.command()
async def spaghetti(ctx):
    await ctx.send('and meatballs')


# Read auth.json
with open('auth.json', 'r') as auth_file:
    data = auth_file.read()

# Convert to a json object
auth = json.loads(data)

# Run Ori using the auth token from 'auth.json'
ori.run(auth['token'])
