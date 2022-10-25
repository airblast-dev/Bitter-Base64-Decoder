import binascii
import discord
from discord import app_commands
import base64
from validators import url as vurl

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
per_reaction = dict()
tree = app_commands.CommandTree(client)


def dict_search(x):  # This is only used for dictionary looping for embedded messages by users or bots
    y = list()

    def dict_search_u(a):
        if type(a) == dict:
            for k, v in a.items():
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
    open('usage.txt', 'a').close()
    open('cache.txt', 'a').close()
    with open('cache.txt', 'r') as file:
        for line in file:
            line = line.split(':', 2)
            line[2] = line[2].replace('\\n', '\n').replace('\\r', '')
            intl = int(line[0])
            if intl not in per_reaction:
                per_reaction[intl] = dict()
            per_reaction[intl][int(line[1])] = line[2]
    await tree.sync()
    print(per_reaction)
    print(f'Bot has been fully started.')


@tree.command(name='encodeb', description='Bitter will encode your message and send it in this channel.')
async def encodebcmd(interaction: discord.Interaction, param: str):
    discord_response = discord.Embed(description=f'{interaction.user} has encoded: {b64enc(param)}')
    await interaction.channel.send(embed=discord_response)
    await interaction.response.send_message("Your message has been encoded.", ephemeral=True)


@tree.command(name='usageb', description='Sends the current number of total uses for Bitter.')
async def usagecmd(interaction: discord.Interaction):
    usage = open('usage.txt', 'r').read()
    discord_response = discord.Embed(title=f'Bitter has been used {usage} times.')
    await interaction.response.send_message(embed=discord_response, ephemeral=True)


@tree.context_menu(name='FindB64')
async def findb64(interaction: discord.Interaction, message: discord.Message):
    words, worde, words = list(), list(), list()
    counter, counterrem = 0, 1
    emoji = '1️⃣'
    worde = message.content.split()
    with open('usage.txt', 'r') as file:
        usage = int(file.read())
        usage += 1
        file = open('usage.txt', 'w')
        file.write(str(usage))
        file.close()
    for embed in message.embeds:
        for item in (dict_search(embed.to_dict())):
            if type(item) != str:
                continue
            if len(item.split()) > 1:
                for word in item.split():
                    worde.append(word)
            else:
                worde.append(item)
    for word in worde:
        if len(words) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len(word) >= 6:
                    words.append(word)
                    counter += 1
                    with open('cache.txt', 'a') as file:
                        file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue
    if len(words):
        int_response = discord.Embed(
            description=f'Bitter was able to find {len(words)} encoded messages.',
            color=0x444444,
        )
    else:
        int_response = discord.Embed(
            description=f'Bitter wasn\'t able to find any encoded messages.',
            color=0x444444,
        )
    await interaction.response.send_message(embed=int_response, ephemeral=True)
    for counterrem in reversed(range(counter + 1, len(per_reaction[message.id]) + 1)):
        emoji = str(counterrem) + emoji[1:]
        await message.clear_reaction(emoji)
    per_reaction[message.id] = dict()
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        emoji = str(counter) + emoji[1:]
        await message.add_reaction(emoji)
        counter += 1
    with open('usage.txt', 'r') as file:
        usage = int(file.read())
        usage += 1
        file = open('usage.txt', 'w')
        file.write(str(usage))


@client.event
async def on_message(message: discord.Message):
    if message.id in per_reaction:
        return
    words, worde = list(), list()
    counter = 0
    worde = message.content.split()
    for embed in message.embeds:
        for item in (dict_search(embed.to_dict())):
            if type(item) != str:
                continue
            if len(item.split()) > 1:
                for word in item.split():
                    worde.append(word)
            else:
                worde.append(item)
    for word in worde:
        if len(words) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len((wordsp := word.split())) >= 1:
                    for item in wordsp:
                        if vurl(item) or vurl('https://' + item):
                            counter += 1
                            with open('cache.txt', 'a') as file:
                                file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                            if counter:
                                words += [word]
                                break
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue  # AttributeError for sticker and gifs and etcetera. The rest is for decode/encode related errors.
    if counter:
        per_reaction[message.id] = dict()
    emoji = '1️⃣'
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        try:  # If the user has blocked the bot, suppress exception and return since bot cant add reaction anyway.
            await message.add_reaction(emoji)
        except:
            return
        counter += 1
        emoji = str(counter) + emoji[1:]


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if str(client.user) == str(payload.member) or \
            payload.emoji.name[1:] != '️⃣':  # Check if user that reacted is the bot itself.
        return
    if payload.message_id in per_reaction and \
            len(per_reaction[payload.message_id]) < int(payload.emoji.name[0:1]):
        return
    with open('usage.txt', 'r') as file:
        usage = int(file.read())
        usage += 1
        file = open('usage.txt', 'w')
        file.write(str(usage))
        file.close()
    if payload.message_id in per_reaction:
        decoded_embed = discord.Embed(
            title='Bitter decoded this to:',
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        try:
            await payload.member.send(embed=decoded_embed)
            return
        except discord.errors.Forbidden:
            pass
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    words, worde = list(), list()
    counter = 0
    worde = message.content.split()
    for embed in message.embeds:
        for item in (dict_search(embed.to_dict())):
            if type(item) != str:
                continue
            if len(item.split()) > 1:
                for word in item.split():
                    worde.append(word)
            else:
                worde.append(item)
    for word in worde:
        if len(words) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len((wordsp := word.split())) >= 1:
                    for item in wordsp:
                        if vurl(item) or vurl('https://' + item):
                            counter += 1
                            with open('cache.txt', 'a') as file:
                                file.write(str(message.id) + ":" + str(counter) + ":" + repr(word)[1:-1] + '\n')
                            if counter:
                                words += [word]
                                break
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue
    if counter:
        per_reaction[payload.message_id] = dict()
    else:
        return
    emoji = '1️⃣'
    counter = 1
    for word in words:
        per_reaction[message.id][counter] = word
        try:  # If the user has blocked the bot, suppress exception and return since bot cant add reaction anyway.
            await message.add_reaction(emoji)
        except:
            return
        counter += 1
        emoji = str(counter) + emoji[1:]
    decoded_embed = discord.Embed(
        title='Bitter decoded this to:',
        description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
        color=0x444444,
    )
    try:  # If user that clicked reaction has blocked the bot, suppress exception.
        await payload.member.send(embed=decoded_embed)
    except:
        pass
    print(per_reaction)


client.run('Your Token')
