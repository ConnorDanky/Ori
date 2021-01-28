import json

import discord


class Ori(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):

        # don't respond to ourselves
        if message.author == self.user:
            return

        # tridecalogism
        if len(message.content) == 13:
            await message.channel.send(':eboy:')


# Read auth.json
with open('auth.json', 'r') as auth_file:
    data = auth_file.read()

auth = json.loads(data)

ori = Ori()
ori.run(auth['token'])
