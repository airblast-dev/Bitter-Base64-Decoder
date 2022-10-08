import discord
from discord import app_commands
import base64
from validators import url as vurl
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
per_reaction = dict()
tree = app_commands.CommandTree(client)


def dict_search(x):
    y = list()

    def dict_search_u(x):
        if type(x) == dict:
            for k, v in x.items():
                if isinstance(v, dict):
                    dict_search_u(v)
                elif isinstance(v, list):
                    for item in v:
                        dict_search_u(item)
                else:
                    y.append(v)

    dict_search_u(x)
    return y


def b64dec(x):
    return (base64.b64decode(x + '==')).decode('ascii')


def b64enc(x):
    return (base64.b64encode(x.encode('ascii'))).decode('ascii')


@client.event
async def on_ready():
    open('cache.txt', 'a').close()
    with open('cache.txt', 'r') as file:
        for line in file:
            line = line.split(':', 2)
            line[2] = line[2].replace('\\n','\n').replace('\\r','')
            intl = int(line[0])
            if int(line[1]) == 1:
                per_reaction[intl] = dict()
            per_reaction[intl][int(line[1])] = line[2]
        print(per_reaction)
    await tree.sync()


@tree.context_menu(name='FindB64')
async def findb64(interaction: discord.Interaction, message: discord.Message):
    words, worde = list(), list()
    counter = 0
    worde = message.content.split()
    for embed in message.embeds:
            worde += (dict_search(embed.to_dict()))
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len(word) >= 6:
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                    with open('auto_log.txt', 'a') as file:
                        now = str(datetime.now()).replace(':', '.')
                        file.write(
                            f'{per_reaction[payload.message_id][counter]}:{now}\n'
                        )
                    words.append(word)
        except:
            continue

    if counter:
        per_reaction[message.id] = dict()
    emoji = '1️⃣'
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        await message.add_reaction(emoji)
        counter += 1
        emoji = str(counter) + emoji[1:]
    if len(words):
        int_response = discord.Embed(
            description=f'Bitter was able to find {len(words)} encoded messages.',
            color=0x444444,
        )
    else:
        int_response = discord.Embed(
            description=f'Bitter wasnt able to find any encoded messages.',
            color=0x444444,
        )
    await interaction.response.send_message(embed=int_response, ephemeral=True)

@client.event
async def on_message(message):
    if message.id in per_reaction:
        return
    words, worde = list(), list()
    counter = 0
    worde = message.content.split()
    for embed in message.embeds:
        worde += (dict_search(embed.to_dict()))
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if vurl(word):
                    words.append(word)
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                elif vurl('https://' + word):
                    words.append('https://' + word)
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                elif len((word := word.split())) > 1:
                    for item in word:
                        if vurl(item) or vurl(item := 'https://' + item):
                            counter += 1
                            with open('cache.txt', 'a') as file:
                                file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                            words.append(item)
        except:
            continue
    if counter:
        per_reaction[message.id] = dict()
    emoji = '1️⃣'
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        await message.add_reaction(emoji)
        counter += 1
        emoji = str(counter) + emoji[1:]


@client.event
async def on_raw_reaction_add(payload):
    if str(client.user) == str(payload.member) or payload.emoji.name[1:] != '️⃣':
        return
    if payload.message_id in per_reaction:
        decoded_embed = discord.Embed(
            title='Bitter decoded this to:',
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        await payload.member.send(embed=decoded_embed)
        with open('auto_log.txt', 'a') as file:
            now = str(datetime.now()).replace(':', '.')
            file.write(
                f'{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n'
            )
        return
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    words, worde = list(), list()
    counter = 0
    worde = message.content.split()
    for embed in message.embeds:
        worde += (dict_search(embed.to_dict()))
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if vurl(word):
                    words.append(word)
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                elif vurl('https://' + word):
                    words.append('https://' + word)
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                elif len((word := word.split())) > 1:
                    for item in word:
                        if vurl(item) or vurl(item := 'https://' + item):
                            counter += 1
                            with open('cache.txt', 'a') as file:
                                file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                            words.append(item)
        except:
            continue
    if counter:
        per_reaction[payload.message_id] = dict()
    else:
        return
    emoji = '1️⃣'
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        await message.add_reaction(emoji)
        counter += 1
        emoji = str(counter) + emoji[1:]
    decoded_embed = discord.Embed(
        title='Bitter decoded this to:',
        description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
        color=0x444444,
    )
    await payload.member.send(embed=decoded_embed)
    with open('auto_log.txt', 'a') as file:
        now = str(datetime.now()).replace(':', '.')
        file.write(
            f'{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n'
        )
    print(per_reaction)


client.run('Your Token')
