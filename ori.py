import json
import os
import random
import time

import discord
import googletrans
from discord.ext import commands
from googletrans import Translator

from prsaw import RandomStuff

import util.io_util as io_util
import util.string_util as string_util

# adding Translator
translator = Translator()

# adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents=intents)

# Banned word list
filtered_words = ["cobner","Cobner"]

# quote lists for member commands
berry_quotes = [
    "achoo", ":yawning_face:", "ez", ":speaking_head:", "a", "A", ":crab: money money money money :crab:",
    "how’d u know :eyes:", "brr", "we got the :b:read", "pfffft", "bonjour", "creenj", "si despacito", "eee",
    "mon nez est maintenant brisé", "il ne marche pas", "je suis pas un garçon?", ":speaking_head:  :speaker: AAAAA",
    "GM :clap: :clap:", "\\*yaaawn\\*", "im filling myself with chicken", "je ne sais pas!", "c'est moi", "merci merci",
    "google translate n'existe pas", "don't wanna mess with bery", "mhm mhm", "now or I'll :punch:", "pretty good mhm",
    "rip the sandwich :pensive:", "all in a day’s work :yawning_face:", "perhaps another time!",
    "can't believe there's no orange team smh", "haven't i told u already to stop talking to urself!", "mwahahaha",
    "grrrr", "i always win", "makes you wonder and ponder...", "SI SI", "love him, or hate him, he be spitting garbage"
]
frozil_quotes = [
    "Creenj", "!work!work!work", ":flushed:", "frozil", "eeeeeeee", "hmmm", "Kinda wanna try girl scout cookies",
    "cringe", "get shit on", "this game is rigger", "bruh", "imagine showering", "When rocket league", "0 points!",
    "Nothing? cringe", "we dont have water down here", "cant relate", "frozil opening u win in 1 move",
    "He's telling u no mimis", "Oh god oh god", "Oh shit", "No mimir",
    "mf made me order mexican stuff and didnt warn me about the hot salsa", "berry looks like a mushroom",
    "berry finna grenade launch akoots ass", "come play!", "Y'all always play when im not home :weary:",
    "Damn I guess im not really wanted *(edited)*", "I'm kidding btw I love rocket league",
    "Imagine playing rocket league", "Don't use robinhood for crypto", "no one likes u\nits the truth :rolling_eyes:",
    "get shit on berry", "GET SHIT ON", "this game is rigged", "frozil always wins",
    "Give me all your money\nThis is not financial advice", "I'm always right", "cant ban me\nim too epic",
    "imagine talking in spanish", "God I love elon musk", "U can't rap through text", "i see how it is",
    "like that huh", "tf is wrong with connor", "I'll 1v1 in rocket league", "elon musk tweeted about dogecoin",
    "america as a whole do be big", "less gooo", "where did u get that picture of me?",
    "im froz, you probably heard of me", "i think i have around 45 doge coins sitting somewhere"
]


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

    # banned words in chat
    for word in filtered_words:
        if word in message.content:
            
            await message.delete()


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

@ori.command(aliases=['d'])
@commands.has_permissions(manage_messages=True)
async def delete(ctx, amount=2):
    await ctx.channel.purge(limit=amount)


# !ticket
@ori.command()
async def ticket(ctx,level,*,message):
    member = ctx.author
    level = level.lower()
    channel = discord.utils.get(member.guild.channels,
                                name="tickets")
    if message == "":
        return
    ticket_high_embed = discord.Embed(
        color=(discord.Color.gold()),
        title=f"TICKET! (submitted by: {member.display_name})",
        description="Importance: HIGH\n" + message + "\n"
    )
    ticket_low_embed = discord.Embed(
        color=(discord.Color.dark_gold()),
        title=f"TICKET! (submitted by: {member.display_name})",
        description="Importance: LOW\n" + message + "\n"
    )
    
    if level == "high":
        await ctx.send("Thanks for your report!")
        await channel.send("<@&823299908105666620>")
        await channel.send(embed = ticket_high_embed)
    if level == "low":
        await ctx.send("Thanks for your report!")
        await channel.send(embed = ticket_low_embed)


# Kicking Members

@ori.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason given!"):
    await member.send(f"You have been kicked from {member.guild.name}, because " + reason)
    await member.send("Come back if you can follow the rules: https://discord.gg/cyTEjWkyMb")
    await member.kick(reason=reason)

# Polls
@ori.command()
@commands.has_role("mod-squad")

async def poll(ctx,question,choices):
    emoteList = ["regional_indicator_a","regional_indicator_b","regional_indicator_c","regional_indicator_d",
    "regional_indicator_e","regional_indicator_f","regional_indicator_g","regional_indicator_h","regional_indicator_i",
    "regional_indicator_j"]

    emoteList2 = ["🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯"]

    choiceList = choices.split("/")
    output = ""
    counter = 0
    for i in choiceList:
        output += ":"+ emoteList[counter] + ":"
        output += f" --- {choiceList[counter]} \n"
        counter += 1

    poll_embed = discord.Embed(
        color=(discord.Color.greyple()),
        title=f"Poll: {question}",
        description= output
    )
    message = await ctx.send(embed = poll_embed)

    emoteCounter = 0
    for i in emoteList2:
        if (emoteCounter < counter):
            await message.add_reaction(i)
            emoteCounter += 1


# !joke command
@ori.command()
async def joke(ctx):

    rs = RandomStuff(async_mode=True)

    joke = await rs.get_joke()

    await ctx.send(joke['setup'])
    time.sleep(3)
    await ctx.send("||" + joke['delivery'] + "||")



# !fort command
@ori.command()
async def fort(ctx):
    fortStr = "<:rLStep:813281418699603968><:rRStep:813282156603768832><:rLStep:813281418699603968><:rRStep:813282156603768832>⬛⬛⬛<:rLStep:813281418699603968><:rRStep:813282156603768832><:rLStep:813281418699603968><:rRStep:813282156603768832>"
    fortStr += "\n<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick:813276220376219690><:rDLStep:813282562067660821>⬛⬛⬛<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick:813276220376219690><:rDLStep:813282562067660821>"
    fortStr += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛⬛⬛<:rBrick:813276220376219690><:rBrick:813276220376219690>⬛"
    fortStr += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rRStep:813282156603768832><:rLStep:813281418699603968><:rBrick:813276220376219690><:rRStep:813282156603768832><:rLStep:813281418699603968><:rBrick:813276220376219690><:rBrick:813276220376219690>"
    fortStr += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690><:rDLStep:813282562067660821>⬛<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>"
    fortStr += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>"
    fortStr += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>"
    await ctx.send(fortStr)

# !berry command
@ori.command()
async def berry(ctx):
    a = random.choice(berry_quotes)
    await ctx.send("<:berry:805607350307782717> - " + a)


# !frozil command
@ori.command()
async def frozil(ctx):
    a = random.choice(frozil_quotes)
    await ctx.send("<:froz:804139444508557372> - " + a)


# translation english command
@ori.command(aliases=["transen", "tre"])
async def translate_en(ctx, *args):
    await translate(ctx, " ".join(args))


# translation command
@ori.command(aliases=["trans", "tr"])
async def translate(ctx, msg, dest="en"):
    msg.lower()
    user = ctx.author
    if msg is "help" and dest is "en":
        lang_list = ""
        for lang in googletrans.LANGUAGES:
            lang_list += (f'{lang} - {googletrans.LANGUAGES[lang]}' + "\n")

        mbed = discord.Embed(color=(discord.Color.blue()), title="Supported Languages for !translation",
                             description=lang_list)
        await user.send(embed=mbed)
    else:

        translation = translator.translate(msg, dest)
        await ctx.send(f'{translation.origin} -> {translation.text}')


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

    m_bed = discord.Embed(title=f"{ctx.author.name}'s balance", color=discord.Color.red())
    m_bed.add_field(name="Points", value=points_amt)
    m_bed.add_field(name="Messages", value=messages_amt)

    await ctx.send(embed=m_bed)


# account systems - points(beg)
@ori.command()
async def work(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_inv_data()

    earnings = random.randrange(101)
    await ctx.send(f"You worked all day and got {earnings} points!!")

    users[str(user.id)]["points"] += earnings

    with open("account.json", "w") as f:
        json.dump(users, f)


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

    with open("account.json", "w") as f:
        json.dump(users, f)
    return True


# account systems - inventory data
async def get_inv_data():
    with open("account.json", "r") as f:
        users = json.load(f)

    return users


# account systems - message counter
async def add_message(caller):
    await open_account(caller)
    user = caller
    users = await get_inv_data()

    users[str(user.id)]["messages"] += 1

    with open("account.json", "w") as f:
        json.dump(users, f)


token_environment_key = "DISCORD_TOKEN"
if token_environment_key in os.environ:
    # Load token from the environment variable
    token = os.environ[token_environment_key]
else:
    # Load auth token from 'auth.json'
    token = io_util.load_json('auth.json')['token']

# Run Ori using the auth token object
ori.run(token)
