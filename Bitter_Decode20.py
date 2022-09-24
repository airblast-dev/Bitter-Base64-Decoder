import discord
import base64
from validators import url as vurl
from datetime import datetime


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
per_reaction = dict()
now = str(datetime.now())


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
async def on_message(message):
    words, worde = list(), list()
    counter = 0
    if len(message.embeds) == 0:  # User messages
        worde = message.content.split()
    else:  # All Embed Messages from Bots
        for embed in message.embeds:
            worde += (dict_search(embed.to_dict()))
    if counter:
        return
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if vurl(word):
                    words.append(word)
                    counter += 1
                elif vurl('https://' + word):
                    words.append('https://' + word)
                    counter += 1
                elif len((word := word.split())) > 1:
                    for item in word:
                        print(vurl(item))
                        if vurl(item) or vurl(item := 'https://' + item):
                            counter += 1
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
            file.write(
                f'{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n'
            )
        return
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    words, worde = list(), list()
    counter = 0
    if len(message.embeds) == 0:  # User messages
        worde = message.content.split()
    else:  # All Embed Messages from Bots
        for embed in message.embeds:
            worde += (dict_search(embed.to_dict()))
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if vurl(word):
                    words.append(word)
                    counter += 1
                elif vurl('https://' + word):
                    words.append('https://' + word)
                    counter += 1
                elif len((word := word.split())) > 1:
                    for item in word:
                        print(vurl(item))
                        if vurl(item) or vurl(item := 'https://' + item):
                            counter += 1
                            words.append(item)
        except:
            continue
    if counter:
        per_reaction[payload.message_id] = dict()
    else:
        return
    print(words)
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
        file.write(
            f'{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n'
        )
    print(per_reaction)
client.run('Your Token')
