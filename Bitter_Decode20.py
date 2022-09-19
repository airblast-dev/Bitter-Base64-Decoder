import discord
import base64
from validators import url as vurl
from datetime import datetime


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
per_reaction = dict()
now = str(datetime.now())


def b64dec(x):
    return (base64.b64decode(x + '==')).decode('ascii')


def b64enc(x):
    return (base64.b64encode(x.encode('ascii'))).decode('ascii')


@client.event
async def on_message(message):
    words, worde = list(), list()
    counter = 0
    if str(message.author) != 'Rezi#8393' and str(message.author) != 'CoveBot#6047':  # User messages
        for word in message.content.split():
            worde.append(word)
    elif str(message.author) == 'Rezi#8393':  # ReziBot support
        for embed in message.embeds:
            embed_dict = embed.to_dict()
            nums = range(0, len(embed_dict['fields']))
            for num in nums:
                if 'fields' in embed_dict \
                        and isinstance(embed_dict['fields'][num], dict) \
                        and 'value' in embed_dict['fields'][num]:
                    worde.append(embed_dict['fields'][num]['value'])
                else:
                    continue
    elif str(message.author) == 'CoveBot#6047':  # CoveBot support
        for embed in message.embeds:
            embed_dict = embed.to_dict()
            if 'fields' in embed_dict \
                    and isinstance(embed_dict['fields'][6], dict) \
                    and 'value' in embed_dict['fields'][6]:
                worde = [x for x in embed_dict['fields'][6]['value'].split()]
            elif 'description' in embed_dict:
                worde = [x for x in embed_dict['description'].split()]
            else:
                continue
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', '') \
                    and vurl(word) or vurl(word := 'https://' + word):
                words.append(word)
                counter += 1
        except:
            continue
    emoji = '1️⃣'
    if counter:
        per_reaction[message.id] = dict()
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        await message.add_reaction(emoji)
        counter += 1
        emoji = str(counter) + emoji[1:]


@client.event
async def on_raw_reaction_add(payload):
    print(per_reaction)
    if str(client.user) == str(payload.member) or payload.emoji.name[1:] != '️⃣':
        return
    if payload.message_id in per_reaction:
        decoded_embed = discord.Embed(
            title='Bitter decoded this to:',
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        await payload.member.send(embed=decoded_embed)
        return
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    per_reaction[payload.message_id] = dict()
    words, worde = list(), list()
    counter = 0
    if str(message.author) != 'Rezi#8393' and str(message.author) != 'CoveBot#6047':  # User messages
        for word in message.content.split():
            worde.append(word)
    elif str(message.author) == 'Rezi#8393':  # ReziBot support
        for embed in message.embeds:
            embed_dict = embed.to_dict()
            nums = range(0, len(embed_dict['fields']))
            for num in nums:
                if 'fields' in embed_dict \
                        and isinstance(embed_dict['fields'][num], dict) \
                        and 'value' in embed_dict['fields'][num]:
                    worde.append(embed_dict['fields'][num]['value'])
                else:
                    continue
    elif str(message.author) == 'CoveBot#6047':  # CoveBot support
        for embed in message.embeds:
            embed_dict = embed.to_dict()
            if 'fields' in embed_dict \
                    and isinstance(embed_dict['fields'][6], dict) \
                    and 'value' in embed_dict['fields'][6]:
                worde = [x for x in embed_dict['fields'][6]['value'].split()]
            elif 'description' in embed_dict:
                worde = [x for x in embed_dict['description'].split()]
            else:
                continue
    for word in worde:
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', '') \
                    and vurl(word) or vurl(word := 'https://' + word):
                words.append(word)
                counter += 1
        except:
            continue
    emoji = '1️⃣'
    if counter:
        per_reaction[payload.message_id] = dict()
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
