import binascii
import pickle
import discord
import base64
from validators import url as vurl
from os.path import isfile

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# Notes for variables: 


# worde = List of every item in embed or user sent messages.

# tempdict = The tempdict variable creates a temporary dictionary to later append or save to a pickle.

# wordsp = Whilst iterating over every item in worde, wordsp stores a split version of the decoded item.

# word = Generally this variable is used to store iterations of worde.


class Files:
    def __init__(self, filename):
        self.filename = filename
        if not isfile(filename):
            with open(filename, 'wb') as file:
                if filename == 'stats.pickle':
                    pickle.dump({'usage': '0'}, file)
                if filename == 'cache.pickle' or filename == 'server_settings.pickle':
                    pickle.dump({'': ''}, file)

    def file(self, item_id: str = None):  # If not argument is entered it will return full pickle.
        with open(self.filename, 'rb') as file:  # If argument is entered pickle file will be read until requested
            tempp = dict()  # item is found.
            cond = bool(item_id)
            while True:
                try:
                    tempp.update(pickle.load(file))
                except EOFError:
                    break
                if cond and item_id in tempp:
                    return tempp[item_id]
            return tempp

    def add(self, dictvar: dict):  # Only dictionary's should be passed -> {str(item_id): setting or decoded item}
        with open(self.filename, 'ab') as file:
            pickle.dump(dictvar, file)

    def save(self, dictvar: dict, item_id: str = None):
        if isinstance(item_id, str):  # This is for situations where editing the file or reading
            tempp = dict()  # the whole file is needed but the whole dictionary does not need to be copied. Essentially
            with open(self.filename, 'rb') as file:  # this is to avoid excess data being sent to a function.
                while True:  # Passing a parameter is preferred where possible.
                    try:
                        tempp.update(pickle.load(file))
                    except EOFError:
                        break
            try:
                with open(self.filename, 'wb') as file:
                    tempp[item_id] = dictvar
                    pickle.dump(tempp, file)
                    return
            except:
                raise KeyError
        with open(self.filename, 'wb') as file:  # If item_id is left blank first item will overwrite anything in pickle
            pickle.dump(dictvar, file)


cache = Files('cache.pickle')
stats = Files('stats.pickle')
server_settings = Files('server_settings.pickle')


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
    per_guild = server_settings.file()
    per_reaction = cache.file()
    for item in client.guilds:
        if (x := str(item.id)) not in per_guild:  # If bot is in servers but not settings are found
            server_settings.add({x: {'UrlB64': True, 'MagnetB64': False, 'TextB64': False}})  # save default settings.
            per_guild.update({x: {'UrlB64': True, 'MagnetB64': False, 'TextB64': False}})
    guild_id_list = [guild.id for guild in client.guilds]
    if len(per_guild) > 1 and '' in per_guild:
        del per_guild['']
    if len(per_reaction) > 1 and '' in per_reaction:
        del per_reaction['']
        cache.save(per_reaction)
    x = dict()
    x.update(per_guild)
    for item in x:  # If bot has been removed from a server whilst offline delete server setting.
        print(item)
        if int(item) not in guild_id_list:
            del per_guild[item]
    server_settings.save(per_guild)
    del per_guild
    del per_reaction
    del x
    del guild_id_list
    await tree.sync()
    print(f'Bot has been fully started.')
    return


@client.event
async def on_guild_join(guild: discord.Guild):
    server_settings.add({str(guild.id): {'UrlB64': True, 'MagnetB64': False, 'TextB64': False}})


@client.event
async def on_guild_remove(guild: discord.Guild):
    per_guild = server_settings.file()
    del per_guild[str(guild.id)]
    server_settings.save(per_guild)


async def toggle_autocomplete(
        _,
        current: str
) -> list[discord.app_commands.Choice[str]]:
    options = ['UrlB64', 'MagnetB64', 'TextB64']
    return [
        discord.app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]


@tree.command(name='toggle', description='This command toggle\'s auto magnet detection' +
                                         ' on or off for the channel its used in.')
@discord.app_commands.autocomplete(option=toggle_autocomplete)
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def toggle(interaction: discord.interactions.Interaction, option: str):
    current_guild = server_settings.file(str(interaction.guild_id))
    if option not in current_guild:
        toggle_response = discord.Embed(
            title='Error: Invalid parameter.',
            description=f'{option} is not a valid parameter.'
        )
        await interaction.response.send_message(embed=toggle_response, ephemeral=True)
        return
    if current_guild[option]:
        current_guild[option] = False
    else:
        current_guild[option] = True
    toggle_response = discord.Embed(
        title=f'{option} has been set to {current_guild[option]}.',
        description='**Current settings:**'
    )
    toggle_response.add_field(name='TextB64', value=f'{current_guild["TextB64"]}')
    toggle_response.add_field(name='UrlB64', value=f'{current_guild["UrlB64"]}')
    toggle_response.add_field(name='MagnetB64', value=f'{current_guild["MagnetB64"]}')
    await interaction.response.send_message(embed=toggle_response, ephemeral=True)
    server_settings.save(current_guild, str(interaction.guild_id))


@toggle.error
async def toggle_error(interaction: discord.Interaction, missing_permissions: discord.app_commands.CommandInvokeError):
    discord_response = discord.Embed(
        title='Error:',
        description=f'{missing_permissions}',
    )
    await interaction.response.send_message(embed=discord_response, ephemeral=True)


@tree.command(name='encodeb', description='Bitter will encode your message and send it in this channel.')
async def encodebcmd(interaction: discord.Interaction, param: str):
    discord_response = discord.Embed(title=f'{interaction.user} has encoded: {b64enc(param)}')
    sent: discord.Message = await interaction.channel.send(
        embed=discord_response)
    try:
        await sent.add_reaction('1️⃣')
    except discord.errors.Forbidden:
        return
    cache.add({str(sent.id): {'1': param}})
    await interaction.response.send_message("Your message has been encoded.", ephemeral=True)


@tree.command(name='usageb', description='Sends the current number of total uses for Bitter.')
async def usagecmd(interaction: discord.Interaction):
    with open('stats.pickle', 'rb') as file:
        stats = pickle.load(file)
    discord_response = discord.Embed(title=f'Bitter has been used {stats["usage"]} times.')
    await interaction.response.send_message(embed=discord_response)


@tree.command(name='help', description='Using this command will send the user a basic command list and explanation.')
async def help_bitter(interaction: discord.Interaction):
    help_response = discord.Embed(title='Basics for Bitter:')
    help_response.add_field(name='/toggle', inline=False, value='The /toggle command will enable specific '
                                                                f'detections based on the user input. For example '
                                                                f'/toggle UrlB64 enable\'s detecting '
                                                                f'base64 encoded Url\'s. Using the command will '
                                                                f'enable it if was disabled and '
                                                                f'disable it if was enabled. Using the command '
                                                                f'will also send a current settings '
                                                                f'list. Currently the bot supports automatic '
                                                                f'TextB64 UrlB64 and MagnetB64 detection.')
    help_response.add_field(name='/encodeb', inline=False,
                            value='The /encodeb command encode\'s any input and sends the '
                                  f'result to the channel that the command was used in. '
                                  f'The output will always be reacted by Bitter.')
    help_response.add_field(name='/usageb', inline=False,
                            value='This command sends how many times Bitter has been used since '
                                  f'November  1st.')
    help_response.add_field(name='Feedback or Suggestions', inline=False, value=f'If you have any feedback or '
                                                                                f'suggestions feel free to reach out '
                                                                                f'to me at: airblast#8095')
    help_response.add_field(name='Source Code', inline=False, value=f'If you would like to see how things actually '
                                                                    f'work you can find the source code at: \n'
                                                                    f'https://github.com/airblast-dev'
                                                                    f'/Bitter-Base64-Decoder'
                            )
    try:
        await interaction.user.send(embed=help_response)
    except discord.errors.Forbidden:
        await interaction.response.send_message(
            'Bitter was not able to send you a message.', ephemeral=True
        )
    else:
        await interaction.response.send_message(
            'Bitter has sent you the response in DM\'s.', ephemeral=True
        )


@tree.context_menu(name='FindB64')
async def findb64(interaction: discord.Interaction, message: discord.Message):
    tempdict = dict()
    counter, botreacted = 0, 1
    emoji = '1️⃣'
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
        if len(tempdict) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len(word) >= 6:
                    counter += 1
                    tempdict[str(counter)] = word
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue
    if tempdict:
        int_response = discord.Embed(
            description=f'Bitter was able to find {len(tempdict)} encoded messages.',
            color=0x444444,
        )
    else:
        int_response = discord.Embed(
            description=f'Bitter wasn\'t able to find any encoded messages.',
            color=0x444444,
        )
    await interaction.response.send_message(embed=int_response, ephemeral=True)
    for reaction in message.reactions:  # Count how many messages the bot has reacted to in the past.
        if not reaction.me:
            botreacted += 1
            if botreacted == 9:
                break
    if botreacted > counter:
        bot = discord.abc.Snowflake
        bot.id = client.application_id
        for counterrem in reversed(range(counter + 1, botreacted + 1)):  # Remove extra reactions.
            try:
                await message.clear_reaction(str(counterrem) + emoji[1:])
            except discord.errors.Forbidden:
                await message.remove_reaction((str(counterrem) + emoji[1:]), bot)
                if botreacted == counterrem:
                    discord_response = discord.Embed(title="Error:",
                                                     description="Bitter was unable to clear extraneous reactions.")
                    discord_response.set_footer(
                        text="Manage messages permission needs to be enabled for Bitter to clear reactions.")
                    await message.channel.send(embed=discord_response, delete_after=10)
    if counter + 1 > botreacted:
        for counter in range(botreacted, len(tempdict) + 1):  # Add new reactions.
            try:
                await message.add_reaction(str(counter) + emoji[1:])
            except discord.errors.Forbidden:
                pass
    per_reaction = cache.file()
    if len(tempdict):  # If any encoded string was found save to dictionary.
        per_reaction[str(message.id)] = tempdict
    elif str(message.id) in per_reaction:
        del per_reaction[str(message.id)]
    cache.save(per_reaction)
    stats.save({'usage': str(int(stats.file()['usage']) + 1)})
    print('FORCE CHECKED B64')


@client.event
async def on_message(message: discord.Message):
    if message.type == discord.MessageType.chat_input_command or isinstance(message.channel, discord.channel.DMChannel):
        return
    current_guild = server_settings.file(str(message.guild.id))
    counter = 0
    tempdict = dict()
    worde = message.content.split()
    emoji = '1️⃣'
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
        if len(tempdict) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len((wordsp := word.split())) >= 1:
                    if current_guild['TextB64'] and len(word) >= 6:
                        counter += 1
                        tempdict[str(counter)] = word
                        continue
                    if current_guild['UrlB64']:
                        for item in wordsp:
                            if vurl(item) or vurl('https://' + item):
                                counter += 1
                                tempdict[str(counter)] = word
                                break
                    if current_guild['MagnetB64']:
                        for item in wordsp:
                            if item.startswith('magnet:?'):
                                counter += 1
                                tempdict[str(counter)] = word
                                break

        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue  # AttributeError for sticker and gifs and etcetera. The rest is for decode/encode related errors.
    if not counter:
        return
    for counter in range(1, len(tempdict) + 1):
        try:
            await message.add_reaction(str(counter) + emoji[1:])
        except discord.errors.Forbidden:
            pass
    cache.add({str(message.id): tempdict})
    print('FOUND B64 IN MESSAGE')


@client.event
async def on_raw_message_edit(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    for reaction in message.reactions:
        if reaction.me:
            break
    else:
        return
    current_guild = server_settings.file(str(message.guild.id))
    counter, botreacted = 0, 1
    tempdict = dict()
    worde = message.content.split()
    emoji = '1️⃣'
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
        if len(tempdict) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len((wordsp := word.split())) >= 1:
                    if current_guild['TextB64'] and len(word) >= 6:
                        counter += 1
                        tempdict[str(counter)] = word
                        continue
                    if current_guild['UrlB64']:
                        for item in wordsp:
                            if vurl(item) or vurl('https://' + item):
                                counter += 1
                                tempdict[str(counter)] = word
                                break
                    if current_guild['MagnetB64']:
                        for item in wordsp:
                            if item.startswith('magnet:?'):
                                counter += 1
                                tempdict[str(counter)] = word
                                break

        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue  # AttributeError for sticker and gifs and etcetera. The rest is for decode/encode related errors.
    if not counter:
        return
    for reaction in message.reactions:  # Count how many messages the bot has reacted to in the past.
        if reaction.me:
            botreacted += 1
            if botreacted == 9:
                break
    if botreacted > counter:
        bot = discord.abc.Snowflake
        bot.id = client.application_id
        for counterrem in reversed(range(counter + 1, botreacted + 1)):  # Remove extra reactions.
            try:
                await message.clear_reaction(str(counterrem) + emoji[1:])
            except discord.errors.Forbidden:
                await message.remove_reaction((str(counterrem) + emoji[1:]), bot)
                if counterrem == counter + 1:
                    discord_response = discord.Embed(title="Error:",
                                                     description="Bitter was unable to clear all extraneous reactions.")
                    discord_response.set_footer(
                        text="Manage messages permission needs to be enabled for Bitter to clear reactions.")
                    await message.channel.send(embed=discord_response, delete_after=10)
    if counter + 1 > botreacted:
        for counter in range(botreacted, len(tempdict) + 1):  # Add new reactions.
            try:
                await message.add_reaction(str(counter) + emoji[1:])
            except discord.errors.Forbidden:
                pass
    per_reaction = cache.file()
    if len(tempdict):  # If any encoded string was found save to dictionary's.
        per_reaction[str(message.id)] = tempdict
    elif str(message.id) in per_reaction:
        del per_reaction[str(message.id)]
    cache.save(per_reaction)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    per_reaction = cache.file()
    if (x := str(payload.message_id)) in per_reaction:
        del per_reaction[x]
    cache.save(per_reaction)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    user = await client.fetch_user(payload.user_id)
    if user.bot or \
            payload.emoji.name[1:] != '️⃣':  # Check if user that reacted is a bot.
        return
    per_reaction = cache.file()
    if str(payload.message_id) in per_reaction and \
            len(per_reaction[str(payload.message_id)]) < int(payload.emoji.name[0:1]):
        return
    stats.save({'usage': str(int(stats.file()['usage']) + 1)})
    if str(payload.message_id) in per_reaction:
        print('WAS IN PER_REACTION')
        decoded_embed = discord.Embed(
            title='Bitter decoded this to:',
            description=per_reaction[str(payload.message_id)][payload.emoji.name[0]],
            color=0x444444,
        )
        try:
            await payload.member.send(embed=decoded_embed)
            return
        except discord.errors.Forbidden:
            return
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    current_guild = server_settings.file(str(message.guild.id))
    counter = 0
    worde = message.content.split()
    tempdict = dict()
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
        if len(tempdict) >= 9:
            break
        try:
            if word.replace('=', '').replace('`', '') == \
                    b64enc(word := b64dec(word.replace('`', ''))).replace('=', ''):
                if len((wordsp := word.split())) >= 1:
                    if current_guild['TextB64'] and len(word) >= 6:
                        counter += 1
                        tempdict[str(counter)] = word
                        continue
                    if current_guild['UrlB64']:
                        for item in wordsp:
                            if vurl(item) or vurl('https://' + item):
                                counter += 1
                                tempdict[str(counter)] = word
                                break
                    if current_guild['MagnetB64']:
                        for item in wordsp:
                            if item.startswith('magnet:?'):
                                counter += 1
                                tempdict[str(counter)] = word
                                break

        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError, binascii.Error, ValueError):
            continue  # AttributeError for sticker and gifs and etcetera. The rest is for decode/encode related errors.
    if counter:
        per_reaction[str(message.id)] = dict()
    else:
        return
    emoji = '1️⃣'
    per_reaction[str(message.id)] = tempdict
    for counter in range(1, len(tempdict) + 1):
        try:  # If the user has blocked the bot, suppress exception and return since bot cant add reaction anyway.
            await message.add_reaction(str(counter) + emoji[1:])
        except discord.errors.Forbidden:
            return
    decoded_embed = discord.Embed(
        title='Bitter decoded this to:',
        description=per_reaction[str(message.id)][payload.emoji.name[0]],
        color=0x444444,
    )
    try:  # If the user that clicked reaction has blocked the bot, suppress exception.
        await payload.member.send(embed=decoded_embed)
    except discord.errors.Forbidden:
        pass
    cache.save(per_reaction)
    print('NOT IN CACHE')


client.run('Your Token')
