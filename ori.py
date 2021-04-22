import json
import os
import random
import re
import time

import discord
import googletrans
import psycopg2
from discord.ext import commands
from googletrans import Translator
from prsaw import RandomStuff

import util.io_util as io_util
import util.string_util as string_util

# my Random-Stuff-api key... (Need to secure this later)
api_key = "WrrMqKwh369g"

# adding Translator
translator = Translator()

# adding intents
intents = discord.Intents().all()

# Create Ori instance
ori = commands.Bot(command_prefix='!', intents=intents)

# Banned word list
filtered_words = ["cobner", "Cobner"]

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

lookup_text = [
    "I am going to find the very best {0} quotes for your enjoyment!",
    "{0} is so cool and has such amazing quotes.. Let me find some real quick!",
    "Hold on, looking up some classic {0} quotes...",
    "Oh, you want a {0} quote? Let me pick some of my favorites...",
    "{0}! Always saying the wackiest stuff.. In fact, I have a list of quotes! let me find it hold on..."
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
    if row is None:
        return default
    else:
        return row[0]


def get_points(member: discord.Member):
    statement = f"SELECT points FROM accounts WHERE id={member.id}"
    db_cursor.execute(statement)
    return fetch_cursor(0)


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
    db_cursor.execute(f"SELECT {key} FROM stats WHERE id=%s", member.id)
    return fetch_cursor("")


def set_stat(member: discord.Member, key: str, value):
    ps = f"INSERT INTO accounts (id, {key}) VALUES ({member.id}, {value}) ON CONFLICT (id) DO UPDATE SET {key}=%s"
    db_cursor.execute(ps, value)
    db_connection.commit()


# get a random message from a Member
async def get_random_message(ctx: discord.ext.commands.Context, person: str):
    guy = peoples[person]
    _id = guy['id']
    if 'messages' in guy:
        messages = guy['messages']
    else:
        await ctx.send(random.choice(lookup_text).format(string_util.upper(person)))
        messages = []
        for channel in ctx.guild.text_channels:
            async for message in channel.history(limit=500):
                if message.author.id == _id and message.content and message.content[0] != '!':
                    if message.content not in messages:
                        messages.append(message.content)
    guy['messages'] = messages
    return random.choice(messages)


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


@ori.command()
async def test6(ctx: discord.ext.commands.Context):
    points = get_points(ctx.author) + 1
    pinecones = get_pinecones(ctx.author) + 1
    print("points:", points, "pinecones:", pinecones)
    set_points(ctx.author, points)
    set_pinecones(ctx.author, pinecones)
    await ctx.send(f"you have {points} points and {pinecones} pinecones.")


# !ticket
@ori.command()
async def ticket(ctx, level, *, message):
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
        await channel.send(embed=ticket_high_embed)
    if level == "low":
        await ctx.send("Thanks for your report!")
        await channel.send(embed=ticket_low_embed)


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
        description=output
    )
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
    rs = RandomStuff(async_mode=True, api_key=api_key)

    _joke = rs.get_joke(_type="dev")

    if _joke['type'] == 'single':
        await ctx.send(_joke['joke'])
    if _joke['type'] == 'twopart':
        await ctx.send(_joke['setup'])
        time.sleep(3)
        await ctx.send("||" + _joke['delivery'] + "||")


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


# account systems - message counter
async def add_message(caller):
    await open_account(caller)
    user = caller
    users = await get_inv_data()

    users[str(user.id)]["messages"] += 1

    with open("account.json", "w") as f:
        json.dump(users, f)


token_environment_key = "DISCORD_TOKEN"
database_url_environment_key = "DATABASE_URL"
if token_environment_key in os.environ:
    # Load token from the environment variable
    token = os.environ[token_environment_key]

    # Load db
    result = re.match(r'\w+://(\w+):(\w+)@([a-z0-9.-]+):(\d+)/(\w+)', os.environ[database_url_environment_key])
    connect_to_db(result.group(3), result.group(2), result.group(1), result.group(2))
else:
    # Load auth token from 'auth.json'
    auth = io_util.load_json('auth.json')
    token = auth['token']
    db = auth['db']
    connect_to_db(db['host'], db['database'], db['username'], db['password'])

# Run Ori using the auth token object
ori.run(token)
