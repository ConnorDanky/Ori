import json
import os
import random
import re
import time
import datetime

import discord
import googletrans
import psycopg2
from discord.ext import commands
from googletrans import Translator
from prsaw import RandomStuff

from mcuuid import MCUUID
from mcuuid.tools import is_valid_minecraft_username

import util.io_util as io_util
import util.string_util as string_util

# custom colours
cBlue = discord.Colour.from_rgb(126, 201, 241)

keys = {}

# adding Translator
translator = Translator()

# adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents=intents)
ori.remove_command("help")

# Banned word list
filtered_words = [
    "cobner", "Cobner"
]

lookup_text = [
    "I am going to find the very best {0} quotes for your enjoyment!",
    "{0} is so cool and has such amazing quotes.. Let me find some real quick!",
    "Hold on, looking up some classic {0} quotes...",
    "Oh, you want a {0} quote? Let me pick some of my favorites...",
    "{0}! Always saying the wackiest stuff.. In fact, I have a list of quotes! let me find it hold on..."
]

main_shop = [
    {"name":"ConnorDanky Bobblehead","price": 0, "description":"Merch"},
    {"name":"Akoot Mousepad","price": 0, "description":"Merch"},
    {"name":"TOAST toaster","price": 0, "description":"Merch"}
]
peoples = io_util.load_json("people.json")

# for key in peoples: print( f"@ori.command()\nasync def {key}(ctx):\n    message = await get_random_message(ctx,
# '{key}')\n    await ctx.send(" f'"> " + message + " *- " + string_util.upper("{key}") + "*")\n')

db_connection = None
db_cursor = None


def connect_to_db(host, database, user, password):
    global db_cursor
    global db_connection
    db_connection = psycopg2.connect(f"host='{host}' dbname='{database}' user='{user}' password='{password}'")
    db_cursor = db_connection.cursor()
    print("connected to", database, "at", host, "as", user)


def disconnect_from_db():
    if db_connection:
        db_connection.close()


def fetch_cursor(default):
    row = db_cursor.fetchone()
    if row is None or row[0] is None:
        return default
    else:
        return row[0]


def get_points(member: discord.Member):
    statement = f"SELECT points FROM accounts WHERE id={member.id}"
    db_cursor.execute(statement)
    return fetch_cursor(0)

def sort_points():
    statement = "SELECT id FROM accounts ORDER BY points;"
    db_cursor.execute(statement)
    return db_cursor.fetchall()


def set_points(member: discord.Member, amount: int):
    ps = f"INSERT INTO accounts VALUES ({member.id}, {amount}, 0, NULL) ON CONFLICT (id) DO UPDATE SET points={amount}"
    print(ps)
    db_cursor.execute(ps)
    db_connection.commit()


def get_pinecones(member: discord.Member):
    db_cursor.execute(f"SELECT pinecones FROM accounts WHERE id={member.id}")
    return fetch_cursor(0)


def set_pinecones(member: discord.Member, amount: int):
    ps = f"INSERT INTO accounts VALUES ({member.id}, 0, {amount}, NULL) ON CONFLICT (id) DO UPDATE SET pinecones={amount}"
    db_cursor.execute(ps)
    db_connection.commit()


def get_inventory(member: discord.Member):
    db_cursor.execute(f"SELECT inventory FROM accounts WHERE id={member.id}")
    return fetch_cursor(0)


def set_inventory(member: discord.Member, inventory: dict):
    db_cursor.execute(f"UPDATE accounts SET inventory=%s WHERE id={member.id}", inventory)
    db_connection.commit()


def get_stat(member: discord.Member, key: str):
    db_cursor.execute(f"SELECT {key} FROM stats WHERE id={member.id}")
    return fetch_cursor(0)


def set_stat(member: discord.Member, key: str, value):
    ps = f"INSERT INTO stats (id, {key}) VALUES ({member.id}, {value}) ON CONFLICT (id) DO UPDATE SET {key}={value}"
    db_cursor.execute(ps)
    db_connection.commit()


# get a random message from a Member
async def get_random_message(ctx: discord.ext.commands.Context, person: str):
    guy = peoples[person]
    _id = guy['id']
    if 'messages' in guy:
        messages = guy['messages']
    else:
        sent_message = await ctx.send(random.choice(lookup_text).format(string_util.upper(person)))
        await sent_message.delete(delay=10)
        messages = []
        for channel in ctx.guild.text_channels:
            async for message in channel.history(limit=500):
                if message.author.id == _id and message.content and message.content[0] != '!':
                    if message.content not in messages:
                        messages.append(message.content)
    guy['messages'] = messages
    return discord.utils.escape_mentions(random.choice(messages))


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

    #await add_message(message.author)
    messages_sent = get_stat(message.author, 'messages_sent') + 1
    set_stat(message.author, 'messages_sent', messages_sent)

    print(messages_sent)

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

@ori.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = '**Still on cooldown**, please try again in {:.2f}s'.format(error.retry_after)
        await ctx.send(msg)


# @ori.command()
# @commands.has_permissions(manage_messages=True)
# async def reload(ctx):
#     aliases = {}
#     for member in ctx.guild.members:
#         aliases[member.id]['aliases'].append(member.display_name)
#

# Easy Message Deleting

@ori.command(aliases=['d'])
@commands.has_permissions(manage_messages=True)
async def delete(ctx, amount=2):
    await ctx.channel.purge(limit=amount)

# testing for the sort points command
@ori.command()
async def test2(ctx):
    print(sort_points())

    pointsList = sort_points()
    outStr = ""
    for i in pointsList:
        outStr = outStr + i + "\n"
    
    print(pointsList)
    await ctx.send(outStr)


@ori.group(invoke_without_command=True)
async def help(ctx):
    help_embed = discord.Embed(title = "Help", description = "Use `!help <command> for extended information on that command" , colour = discord.Colour.from_rgb(217, 214, 206))

    help_embed.add_field(name = "Moderation", value = "kick, delete, stats, chelp, colour, balance")
    help_embed.add_field(name = "Utility", value = "skin, trans, ud, define, ticket")
    help_embed.add_field(name = "Fun", value = "slots, fort, work")

    await ctx.send(embed = help_embed)

@ori.command()
async def chelp(ctx):
    role_embed = discord.Embed(title="Colour Help!", colour = discord.Colour.from_rgb(49, 195, 72), description = "To change the colour type `!colour [emoji]` with the correct emoji!")
    role_embed.add_field(name="🥶", value = "<@&837548121504481330>")
    role_embed.add_field(name="🐋", value = "<@&837549614664122418>")
    role_embed.add_field(name="🌿", value = "<@&837550801931993128>")
    role_embed.add_field(name="🍌", value = "<@&837551549315153981>")
    role_embed.add_field(name="🍋", value = "<@&837552083330269194>")
    role_embed.add_field(name="🥥", value = "<@&837554703456927744>")
    role_embed.add_field(name="🍊", value = "<@&837555150037844001>")
    role_embed.add_field(name="🌶️", value = "<@&837555829405777951>")
    role_embed.add_field(name="🍎", value = "<@&837556288891387915>")
    role_embed.add_field(name="🍧", value = "<@&837556813825572904>")
    role_embed.add_field(name="🍉", value = "<@&837557343146868757>")
    role_embed.add_field(name="🍇", value = "<@&837557729777811458>")

    await ctx.send(embed = role_embed)

# Colour changing features
@ori.command(aliases = ['color','colours','colors'])
async def colour(ctx, colourRole):

    blueberry_jam = ctx.guild.get_role(837548121504481330)
    blue_raspberry = ctx.guild.get_role(837549614664122418)
    wintergreen_mint = ctx.guild.get_role(837550801931993128)
    banana_split = ctx.guild.get_role(837551549315153981)
    lemonade = ctx.guild.get_role(837552083330269194)
    toasted_coconut = ctx.guild.get_role(837554703456927744)
    peach_tea = ctx.guild.get_role(837555150037844001)
    chili_pepper = ctx.guild.get_role(837555829405777951)
    fuji_apple = ctx.guild.get_role(837556288891387915)
    dragonfruit = ctx.guild.get_role(837556813825572904)
    watermelon_slushie = ctx.guild.get_role(837557343146868757)
    grape_soda = ctx.guild.get_role(837557729777811458)

    role_list = [blueberry_jam,blue_raspberry,wintergreen_mint,banana_split,lemonade,toasted_coconut,
    peach_tea,chili_pepper,fuji_apple,dragonfruit,watermelon_slushie,grape_soda]

    member = ctx.author

    role_dict = {
        "clear" : "no-role",
        "🥶" : blueberry_jam,
        "🐋" : blue_raspberry,
        "🌿" : wintergreen_mint,
        "🍌" : banana_split,
        "🍋" : lemonade,
        "🥥" : toasted_coconut,
        "🍊" : peach_tea ,
        "🌶️" : chili_pepper ,
        "🍎" : fuji_apple ,
        "🍧" : dragonfruit ,
        "🍉" : watermelon_slushie ,
        "🍇" : grape_soda
    }

    role = role_dict[colourRole]

    for i in role_list:
            await member.remove_roles(i)

    if (role != "no-role"):
        await member.add_roles(role)
        await ctx.send(member.mention + f" is now @{role}")
               
    else:
        await ctx.send("Colour set to clear!")


# @ori.command()
# async def test6(ctx: discord.ext.commands.Context):
#     messages_sent = get_stat(ctx.author, 'messages_sent')
#     slots_wins = get_stat(ctx.author, 'slots_wins')
#     print("messages_sent:", messages_sent, "slots_wins:", slots_wins)
#     set_stat(ctx.author, 'messages_sent', messages_sent + 1)
#     set_stat(ctx.author, 'slots_wins', messages_sent + 2)
#     await ctx.send(f"you have {messages_sent} messages sent and {slots_wins} slots wins.")


# !ticket
@ori.command()
async def ticket(ctx, level, *, message):
    print(level)
    print(message)
    member = ctx.author
    level = level.lower()
    tick_channel = discord.utils.get(member.guild.channels,
                                name="tickets")
    if message == "":
        return
    
    if level == "high":
        print("1")
        ticket_embed = discord.Embed(
                color=(discord.Color.gold()),
                title=f"TICKET! (submitted by: {member.display_name})",
                description="Importance: HIGH\n" + message + "\n",
                timestamp = datetime.datetime.utcnow()
            )
        print('2')
        ticket_embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")
        print('3')
        
        print('4')
        await ctx.channel.purge(limit=1)
        await ctx.send("Thanks for your report!")
        await tick_channel.send("<@&841459439655583764>")
        await tick_channel.send(embed=ticket_embed)

    elif level == "low":

        ticket_embed = discord.Embed(
            color=(discord.Color.dark_gold()),
            title=f"TICKET! (submitted by: {member.display_name})",
            description="Importance: LOW\n" + message + "\n",
            timestamp = datetime.datetime.utcnow()
        )
        ticket_embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")
        ticket_embed.timestamp = datetime.datetime.utcnow()

        await ctx.channel.purge(limit=1)
        await ctx.send("Thanks for your report!")
        await tick_channel.send(embed=ticket_embed)


# Kicking Members

@ori.command(aliases=['k'])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason given!"):
    await member.send(f"You have been kicked from {member.guild.name}, because " + reason)
    await member.send("Come back if you can follow the rules: https://discord.gg/cyTEjWkyMb")
    await member.kick(reason=reason)


# Polls
@ori.command()
# @commands.has_role("mod-squad")
async def poll(ctx, question, choices):
    emote_list = ["regional_indicator_a", "regional_indicator_b", "regional_indicator_c", "regional_indicator_d",
                  "regional_indicator_e", "regional_indicator_f", "regional_indicator_g", "regional_indicator_h",
                  "regional_indicator_i",
                  "regional_indicator_j"]

    emote_list2 = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]

    choice_list = choices.split("/")
    output = ""
    counter = 0
    
    for i in choice_list:
        output += ":" + emote_list[counter] + ":"
        output += f" --- {choice_list[counter]} \n"
        counter += 1

    poll_embed = discord.Embed(
        color=(discord.Color.greyple()),
        title=f"Poll: {question}",
        description=output,
        timestamp = datetime.datetime.utcnow()
    )
    poll_embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")
    message = await ctx.send(embed=poll_embed)

    emote_counter = 0
    for i in emote_list2:
        if emote_counter < counter:
            await message.add_reaction(i)
            emote_counter += 1



@ori.command()
async def connor(ctx):
    message = await get_random_message(ctx, 'connor')
    await ctx.send("> " + message + " *- " + string_util.upper("connor") + "*")


@ori.command()
async def akoot(ctx):
    message = await get_random_message(ctx, 'akoot')
    await ctx.send("> " + message + " *- " + string_util.upper("akoot") + "*")


# !joke command
@ori.command()
async def joke(ctx):
    rs = RandomStuff(async_mode=True, api_key=keys['random_stuff'])

    joke = rs.get_joke(_type="dev")

    if joke['type'] == 'single':
        await ctx.send(joke['joke'])
    if joke['type'] == 'twopart':
        await ctx.send(joke['setup'])
        time.sleep(3)
        await ctx.send("||" + joke['delivery'] + "||")


# !fort command
@ori.command()
async def fort(ctx):
    fort_str = "<:rLStep:813281418699603968><:rRStep:813282156603768832><:rLStep:813281418699603968><:rRStep" \
               ":813282156603768832>⬛⬛⬛<:rLStep:813281418699603968><:rRStep:813282156603768832><:rLStep" \
               ":813281418699603968><:rRStep:813282156603768832> "
    fort_str += "\n<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick:813276220376219690><:rDLStep" \
                ":813282562067660821>⬛⬛⬛<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick" \
                ":813276220376219690><:rDLStep:813282562067660821> "
    fort_str += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛⬛⬛<:rBrick:813276220376219690><:rBrick" \
                ":813276220376219690>⬛ "
    fort_str += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rRStep:813282156603768832><:rLStep" \
                ":813281418699603968><:rBrick:813276220376219690><:rRStep:813282156603768832><:rLStep" \
                ":813281418699603968><:rBrick:813276220376219690><:rBrick:813276220376219690> "
    fort_str += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690><:rDLStep" \
                ":813282562067660821>⬛<:rDRStep:813282507079680031><:rBrick:813276220376219690><:rBrick" \
                ":813276220376219690><:rBrick:813276220376219690> "
    fort_str += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛<:rBrick" \
                ":813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690> "
    fort_str += "\n⬛<:rBrick:813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690>⬛⬛⬛<:rBrick" \
                ":813276220376219690><:rBrick:813276220376219690><:rBrick:813276220376219690> "
    await ctx.send(fort_str)


@ori.command()
async def berry(ctx):
    message = await get_random_message(ctx, 'berry')
    await ctx.send("> " + message + " *- " + string_util.upper("berry") + "*")


@ori.command()
async def frozil(ctx):
    message = await get_random_message(ctx, 'frozil')
    await ctx.send("> " + message + " *- " + string_util.upper("frozil") + "*")


@ori.command()
async def sammi(ctx):
    message = await get_random_message(ctx, 'sammi')
    await ctx.send("> " + message + " *- " + string_util.upper("sammi") + "*")


@ori.command()
async def toast(ctx):
    message = await get_random_message(ctx, 'toast')
    await ctx.send("> " + message + " *- " + string_util.upper("toast") + "*")


@ori.command()
async def kate(ctx):
    message = await get_random_message(ctx, 'kate')
    await ctx.send("> " + message + " *- " + string_util.upper("kate") + "*")


@ori.command()
async def xal(ctx):
    message = await get_random_message(ctx, 'xal')
    await ctx.send("> " + message + " *- " + string_util.upper("xal") + "*")


@ori.command()
async def bguette(ctx):
    message = await get_random_message(ctx, 'bguette')
    await ctx.send("> " + message + " *- " + string_util.upper("bguette") + "*")


@ori.command()
async def robin(ctx):
    message = await get_random_message(ctx, 'robin')
    await ctx.send("> " + message + " *- " + string_util.upper("robin") + "*")


@ori.command()
async def pipe(ctx):
    message = await get_random_message(ctx, 'pipe')
    await ctx.send("> " + message + " *- " + string_util.upper("pipe") + "*")


@ori.command()
async def ezek(ctx):
    message = await get_random_message(ctx, 'ezek')
    await ctx.send("> " + message + " *- " + string_util.upper("ezek") + "*")


@ori.command()
async def zythose(ctx):
    message = await get_random_message(ctx, 'zythose')
    await ctx.send("> " + message + " *- " + string_util.upper("zythose") + "*")


@ori.command()
async def yoda(ctx):
    message = await get_random_message(ctx, 'yoda')
    await ctx.send("> " + message + " *- " + string_util.upper("yoda") + "*")


@ori.command()
async def tizzle(ctx):
    message = await get_random_message(ctx, 'tizzle')
    await ctx.send("> " + message + " *- " + string_util.upper("tizzle") + "*")


@ori.command()
async def caleb(ctx):
    message = await get_random_message(ctx, 'caleb')
    await ctx.send("> " + message + " *- " + string_util.upper("caleb") + "*")


# # !berry command
# @ori.command()
# async def berry(ctx):
#     a = random.choice(berry_quotes)
#     await ctx.send("<:berry:805607350307782717> - " + a)
#
#
# # !frozil command
# @ori.command()
# async def frozil(ctx):
#     a = random.choice(frozil_quotes)
#     await ctx.send("<:froz:804139444508557372> - " + a)


# translation english command
@ori.command(aliases=["transen", "tre"])
async def translate_en(ctx, *args):
    await translate(ctx, " ".join(args))


# translation command
@ori.command(aliases=["trans", "tr"])
async def translate(ctx, msg, dest="en"):
    msg.lower()
    user = ctx.author
    if msg == "help" and dest == "en":
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

# admin tool to help resolve issues
@ori.command()
async def aud(ctx,user: discord.Member,key,*,value):
    # Checks to see if its ConnorDanky_
    if ctx.author.id == 435993495627628545:
        if key == "points":
            set_points(user,value)
        elif key == "messages":
            set_stat(user, 'messages_sent', value)
        elif key == "slotwin":
            set_stat(user, 'slots_wins', value)
        elif key == "pinecone":
            set_pinecones(user, value)

# admin tool to help check users stats/points
@ori.command()
async def epm(ctx,user: discord.Member):
    # Checks to see if its ConnorDanky_
    if ctx.author.id == 435993495627628545:
        a = get_points(user)
        b = get_stat(user, 'messages_sent')
        c = get_stat(user, 'slots_wins')
        d = get_pinecones(user)

        em = discord.Embed(title=f"{user.display_name}'s server info")
        em.add_field(name = "Points", value = a)
        em.add_field(name = "Messages Sent", value = b)
        em.add_field(name = "Slot Wins", value = c)
        em.add_field(name = "Pinecones", value = d)
        em.set_thumbnail(url = user.avatar_url)

        await ctx.send(embed = em)

# Slot bars
slot_bars = [':ringed_planet:', ':mushroom:', ':rainbow:', '<:opog:808534536270643270>', ':gem:']

# Slot Machine - Purely for money. 
@ori.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def slots(ctx,*,bet = 1):
    user = ctx.author
    points = get_points(user)

    final = []
    if (bet < 1):
        await ctx.send("The bet must be at least 1 point!")
    if (points >= bet) and (bet > 0):
        for i in range(3):
            a = random.choice(slot_bars)
            final.append(a)
        await ctx.send("".join(final))
        points -= bet

        if all(element == final[0] for element in final):
            slots_wins = get_stat(user,'slots_wins') + 1
            winnings = bet * 15
            await ctx.send(user.mention + f" won {winnings} point(s)! They have won: " + str(slots_wins) + " times." + '<:opog:808534536270643270>')
            set_stat(user,'slots_wins', slots_wins)
            points += winnings
            
        else:
            await ctx.send(f"You lost {bet} point(s). Better Luck next time!")
            
    else:
        await ctx.send("You don't have enough points to make that bet.")

    set_points(user,points)


# main shop
@ori.command(aliases=["shoppe"])
async def shop(ctx):
    em = discord.Embed(title = "Shop")

    for item in main_shop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]

        em.add_field(name = name, value = f"${price}|{desc}")
    await ctx.send(embed = em)


# account systems - balance
@ori.command(aliases=['bal'])
async def balance(ctx):
    # await open_account(ctx.author)
    user = ctx.author
    # users = await get_inv_data()

    # points_amt = users[str(user.id)]["points"]
    # messages_amt = users[str(user.id)]["messages"]

    points_amt = get_points(user)
    pinecone_amt = get_pinecones(user)

    m_bed = discord.Embed(title=f"{ctx.author.name}'s balance", color=discord.Colour.from_rgb(128, 161, 212))
    m_bed.add_field(name="Points", value=points_amt)
    m_bed.add_field(name="Pinecones", value=pinecone_amt)

    await ctx.send(embed=m_bed)

# minecraft skin lookup tool
@ori.command()
async def skin(ctx,*,entry):

    switch = is_valid_minecraft_username(entry)

    try:
        Player = MCUUID(name = entry)
        id_ = Player.uuid

        skin_Embed = discord.Embed(
            colour = (discord.Colour.from_rgb(64, 221, 77)),
            title = entry
        )        
        
        skin_Embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")
        skin_Embed.set_image(url = f'https://visage.surgeplay.com/full/512/{id_}.png')
        skin_Embed.set_thumbnail(url = f'https://visage.surgeplay.com/skin/{id_}.png')
        await ctx.send(embed = skin_Embed)
    except:
        fail_Embed = discord.Embed(
            colour = (discord.Colour.from_rgb(208, 37, 57)),
            title = f"❌ user ({entry}) is not a valid minecraft username!"
        )
        fail_Embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")
        await ctx.send(embed = fail_Embed)

# message totals - slots wins
@ori.command()
async def stats(ctx):
    messages_sent = get_stat(ctx.author, 'messages_sent')
    slots_wins = get_stat(ctx.author,'slots_wins')
    m_bed = discord.Embed(title=f"{ctx.author.name}'s Stats", colour = discord.Colour.from_rgb(126, 201, 241))
    m_bed.add_field(name="Messages", value = messages_sent)
    m_bed.add_field(name="Slots Wins", value = slots_wins)
    m_bed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author}")

    await ctx.send(embed = m_bed)


# account systems - points(beg)
@ori.command()
@commands.cooldown(1,60,commands.BucketType.user)
async def work(ctx):
    # await open_account(ctx.author)
    # user = ctx.author
    # users = await get_inv_data()

    # users[str(user.id)]["points"] += earnings

    # with open("account.json", "w") as f:
        # json.dump(users, f)

    earnings = random.randrange(101)
    await ctx.send(f"You worked all day and got {earnings} points!!")

    user_points = get_points(ctx.author) + earnings
    set_points(ctx.author,user_points)
    print(user_points)

# account systems - opening account
async def open_account(user):
    users = await get_inv_data()

    # checks if an account exists
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


# Links!
@ori.command()
async def links(ctx):
    link_embed = discord.Embed(title="Important Links!", color=discord.Colour.from_rgb(99, 69, 138))
    link_embed.add_field(name="YouTube", value="https://www.youtube.com/channel/UCRG6rfEALDLTVSV52ttR7UQ", inline = True)
    link_embed.add_field(name="Twitch", value ="https://www.twitch.tv/connordanky1", inline = True)
    link_embed.add_field(name="Twitter", value = "https://twitter.com/connor_danky")
    link_embed.add_field(name="Git Hub", value = "https://github.com/ConnorDanky")
    link_embed.add_field(name="Reddit", value = "https://www.reddit.com/r/ConnorDanky/")
    link_embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/773395896264163368/837545034550345778/unknown.png")
    
    await ctx.send(embed = link_embed)

# account systems - message counter
# async def add_message(caller):
    # await open_account(caller)
    # user = caller
    # users = await get_inv_data()

    # users[str(user.id)]["messages"] += 1

    # with open("account.json", "w") as f:
        # json.dump(users, f)
        
    #

discord_token_environment_key = "DISCORD_TOKEN"
random_stuff_token_environment_key = "RANDOM_STUFF_KEY"
database_url_environment_key = "DATABASE_URL"
if discord_token_environment_key in os.environ:
    # Load token from the environment variable

    keys['discord'] = os.environ[discord_token_environment_key]

    keys['random_stuff'] = os.environ[random_stuff_token_environment_key]

    # Load db
    result = re.match(r'\w+://(\w+):(\w+)@([a-z0-9.-]+):(\d+)/(\w+)', os.environ[database_url_environment_key])
    connect_to_db(result.group(3), result.group(5), result.group(1), result.group(2))
else:
    # Load auth token from 'auth.json'
    auth = io_util.load_json('auth.json')

    keys['discord'] = auth['discord_token']

    keys['random_stuff'] = auth['random_stuff_key']

    db = auth['db']
    connect_to_db(db['host'], db['database'], db['username'], db['password'])

# Run Ori using the auth token object
ori.run(keys['discord'])
