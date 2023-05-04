import discord
from discord import (
    Intents,
    Client,
    app_commands,
    ui,
    ButtonStyle,
    Interaction,
    Embed,
    Message,
    Guild,
)
from dotenv import load_dotenv

load_dotenv()

from modules import BitterDB
from modules.extractor import extract_all
from modules.statics import Emoji, Encodings
from modules.encodes import check_all, operations
from modules.templates import Settings
from os import getenv
from modules.message_queue import MessageQueue
from datetime import datetime
import asyncio


intents = Intents()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True
intents.reactions = True
intents.presences = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)


encoding_choices = [
    app_commands.Choice(name=name, value=name) for name in Encodings.names
]

queue = MessageQueue()


db = BitterDB(getenv("CONNECTION_STR"), getenv("DATABASE_NAME"))


class ActivityNormal(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = "servers for new encoded messages!"
        self.type = discord.ActivityType.watching


class ActivityHighLoad(discord.Activity):
    def __init__(self):
        super().__init__()
        self.name = f"Currently under high load!"
        self.type = discord.ActivityType.playing


class DecodeResponse(Embed):
    def __init__(self, content: list[str], jump_url: str, index: int = -1):
        super().__init__()
        self.title = "Bitter decoded this to:"
        if index == -1:
            self.description = "\n".join(content)
        else:
            self.description = content[index]
        self.add_field(
            name="Original message:", value=f"[Click here]({jump_url})", inline=False
        )


async def update_reactions(old_len: int, new_len: int, message: discord.Message):
    if new_len > old_len:
        for emoji in Emoji.numbers[old_len:new_len]:
            await message.add_reaction(emoji)
    elif old_len > new_len:
        reversed_emojis = Emoji.numbers[new_len:old_len]
        reversed_emojis.reverse()
        for emoji in reversed_emojis:
            await message.remove_reaction(emoji, client.user)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.emoji.name not in Emoji.numbers or payload.user_id == client.user.id:
        return
    index = Emoji.numbers.index(payload.emoji.name)
    message_info = db.find_content(
        payload.guild_id, payload.channel_id, payload.message_id
    )
    if message_info is None:
        print("Message was not in DB.")
        channel = client.get_channel(payload.channel_id) or await client.fetch_channel(
            payload.channel_id
        )
        message = await channel.fetch_message(payload.message_id)
        settings = db.get_guild_settings(payload.guild_id)
        content = check_all(extract_all(message), settings)
        if len(content) == 0:
            return
        guild_id = (
            message.guild.id
            if hasattr(message, "guild") and hasattr(message.guild, "id")
            else None
        )
        db.insert_content(guild_id, channel.id, message.id, content, message.jump_url)
        message_info = {"content": content, "jump_url": message.jump_url}
        if len(content) <= index:
            return
    else:
        print("Message ID was in DB.")
    if len(message_info["content"]) <= index:
        return
    user = client.get_user(payload.user_id) or await client.fetch_user(payload.user_id)
    queue.append(
        (
            user,
            DecodeResponse(message_info["content"], message_info["jump_url"], index),
            datetime.now(),
        )
    )
    if queue.high_load is True and client.user.status == discord.Status.online:
        client.change_presence(status=discord.Status.dnd, activity=ActivityNormal())


@client.event
async def on_message(message: discord.Message):
    if isinstance(message.guild, Guild):
        settings = db.get_guild_settings(message.guild.id)
    else:
        settings = {
            key: Encodings.complete[key]["default"] for key in Encodings.complete.keys()
        }
    content = check_all(extract_all(message), settings)
    if len(content) == 0:
        return
    guild_id = (
        message.guild.id
        if hasattr(message, "guild") and hasattr(message.guild, "id")
        else None
    )
    db.insert_content(
        guild_id, message.channel.id, message.id, content, message.jump_url
    )
    # If count is zero no emoji's will be added.
    for emoji in Emoji.numbers[0 : len(content)]:
        await message.add_reaction(emoji)


@tree.command(
    name="settings", description="Enable and disable detections for encoding content."
)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.choices(encoding=encoding_choices)
async def settings(
    interaction: discord.Interaction, encoding: app_commands.Choice[str]
):
    encoding = encoding.value

    def refresh_settings_view(settings: Settings) -> ui.View:
        view = ui.View(timeout=180)
        for check in settings.keys():
            button = ui.Button(label=check.capitalize())
            if settings[check] is True:
                button.style = ButtonStyle.green
                button.callback = set_disable_callback
            elif settings[check] is False:
                button.style = ButtonStyle.red
                button.callback = set_enable_callback
            elif settings[check] is None:
                button.style = ButtonStyle.red
                button.disabled = True
            button.custom_id = check
            view.add_item(button)
        return view

    async def set_enable_callback(interaction: Interaction):
        settings = db.edit_guild_settings(
            interaction.guild.id, encoding, interaction.data["custom_id"], new=True
        )[encoding]
        await interaction.response.edit_message(view=refresh_settings_view(settings))

    async def set_disable_callback(interaction: Interaction):
        settings = db.edit_guild_settings(
            interaction.guild.id, encoding, interaction.data["custom_id"], new=False
        )[encoding]
        await interaction.response.edit_message(view=refresh_settings_view(settings))

    view = ui.View(timeout=180)
    settings = db.get_guild_settings(interaction.guild.id)[encoding]
    view = refresh_settings_view(settings)
    embed = Embed(
        title=f"Settings for {encoding} detections",
        description=Encodings.complete[encoding]["description"],
    )
    await interaction.response.send_message(
        embed=embed, view=view, delete_after=300, ephemeral=True
    )


@settings.error
async def settings_error(interaction: Interaction, error):
    embed = Embed(title="Incorrect permissions", description=error)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    channel = client.get_channel(payload.channel_id) or await client.fetch_channel(
        payload.channel_id
    )
    try:
        message = await channel.fetch_message(payload.message_id)
    except:
        return
    if message.author.id == client.user.id:
        return
    settings = db.get_guild_settings(payload.guild_id)
    content = check_all(extract_all(message), settings)
    old_len = 0
    if len(content) == 0:
        db.delete_content(
            payload.guild_id, payload.channel_id, payload.message_id, content
        )
        message.reactions.reverse()
        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id == client.user.id and reaction.emoji in Emoji.numbers:
                    await message.remove_reaction(reaction.emoji, client.user)
                    break
        return
    else:
        for reaction in message.reactions:
            async for user in reaction.users():
                if user.id == client.user.id and reaction.emoji in Emoji.numbers:
                    old_len += 1
                    break
    guild_id = (
        message.guild.id
        if hasattr(message, "guild") and hasattr(message.guild, "id")
        else None
    )
    result = db.edit_content(
        guild_id, channel.id, message.id, content, message.jump_url
    )
    if result is False:
        db.insert_content(
            guild_id, payload.channel_id, payload.message_id, content, message.jump_url
        )
    new_len = len(content)
    await update_reactions(old_len=old_len, new_len=new_len, message=message)


@tree.command(name="encode", description="Encode an url or any other content.")
@app_commands.choices(encoding=encoding_choices)
async def encode(interaction: discord.Interaction, content: str, encoding: str = None):
    if encoding is None:
        encoding = "Base64"
    encoded = operations[encoding].encode_str(content)
    if encoded is None:
        embed = Embed(
            title=f"Error",
            description=f"{client.user.name} was unable to encode this. \n"
            + f"Please try using [this]({Encodings.complete[encoding]['link']}) instead.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    pfp = (
        interaction.user.guild_avatar
        if hasattr(interaction.user, "guild_avatar")
        else interaction.user.avatar
    )
    pfp = pfp.url if hasattr(pfp, "url") else None
    author = f"{interaction.user.name}#{interaction.user.discriminator}"
    embed = Embed(description=encoded)
    embed.set_footer(icon_url=pfp, text=f"Encoded by {author}")
    message = await interaction.channel.send(embed=embed)
    await interaction.response.send_message(
        embed=Embed(
            title="Succesfully Encoded",
            description=f"{client.user.name} was able to encode message.",
        ),
        ephemeral=True,
    )
    db.insert_content(
        interaction.guild_id,
        interaction.channel.id,
        message.id,
        [content],
        message.jump_url,
    )
    await message.add_reaction(Emoji.numbers[0])


@tree.context_menu(name="Decode Message")
async def decode_message(interaction: Interaction, message: Message):
    await interaction.respose.defer(ephemeral=True)
    message_info = db.find_content(
        interaction.guild.id, interaction.channel.id, message.id
    )
    if message_info is None:
        print("Message was not in DB.")
        settings = db.get_guild_settings(message.guild.id)
        content = check_all(extract_all(message), settings)
        if len(content) == 0:
            embed = Embed(
                title=f"{client.user.name} was unable to find any encoded content",
                description="If you believe this is an error please create an issue on github.",
            )
            await interaction.response.send_message(embed, ephemeral=True)
            return
        guild_id = (
            message.guild.id
            if hasattr(message, "guild") and hasattr(message.guild, "id")
            else None
        )
        db.insert_content(
            interaction.guild.id,
            interaction.channel.id,
            message.id,
            content,
            message.jump_url,
        )
        message_info = {"content": content, "jump_url": message.jump_url}
    else:
        print("Message ID was in DB.")
    user = client.get_user(interaction.user.id) or client.fetch_user(
        interaction.user.id
    )
    await user.send(
        embed=DecodeResponse(
            message_info["content"], message_info["jump_url"], ephemeral=True
        )
    )


@tree.context_menu(name="Refresh Detections")
async def refresh(interaction: Interaction, message: Message):
    await interaction.response.defer(ephemeral=True)
    settings = db.get_guild_settings(interaction.guild_id)
    content = check_all(extract_all(message), settings)
    old_len = 0
    for reaction in message.reactions:
        async for user in reaction.users():
            if user == client.user and reaction.emoji in Emoji.numbers:
                old_len += 1
    new_len = len(content)
    guild_id = (
        message.guild.id
        if hasattr(message, "guild") and hasattr(message.guild, "id")
        else None
    )
    edited = db.edit_content(
        guild_id, message.channel.id, message.id, content, message.jump_url
    )
    if edited is False:
        db.insert_content(
            guild_id, message.channel.id, message.id, content, message.jump_url
        )
    await update_reactions(old_len, new_len, message)
    embed = Embed(
        title="Refresh completed",
        description="Refresh has been completed and reactions have been updated.",
    )
    embed.add_field(name="Old detections", value=str(old_len))
    embed.add_field(name="New detections", value=str(new_len))
    await interaction.followup.send(embed=embed, ephemeral=True)


@tree.command(name="help", description=f"A plain ol help command.")
async def help(interaction: Interaction):
    help_response = Embed(
        title=f"Basics for {client.user.name}:",
        description=f"{client.user.name} is a bot that supports Base64"
        + f" and basE91 content detection based on the guilds settings. The bot currently supports text, urls and magnets."
        + f" By clicking on a reaction that was sent by {client.user.name} you will receive the content or contents from the original message in a decoded state.",
    )
    help_response.add_field(
        name="/help", value="The /help command simply sends this message.", inline=False
    )
    help_response.add_field(
        name="/encode",
        value=f"The /encode command can encode any string to ({', '.join(Encodings.names)}) depending on what you input."
        + "If no option is selected the input will be encoded to Base64. The response from the bot will contain the original sender in the footer section.",
        inline=False,
    )
    help_response.add_field(
        name="/settings",
        value=f"The /settings command allows you to change detections for ({', '.join(Encodings.names)})."
        + " Once you enter the command you click on the buttons below the message it will enable/disable the detection."
        + " Green means the setting is enabled and Red means its disabled.",
    )
    help_response.add_field(
        name="Feedback or Suggestions",
        value="If you have any feedback or suggestions,"
        + " feel free to create an issue on github or shoot me a DM.",
        inline=False,
    )
    help_response.add_field(
        name="Source Code",
        value="If you would like to see how it works in the background you can find the source code at: "
        + "https://github.com/airblast-dev/Bitter-Base64-Decoder",
        inline=False,
    )
    await interaction.response.send_message(embed=help_response, ephemeral=True)


@client.event
async def on_guild_join(guild: Guild):
    db.add_guild(guild)
    db.add_channels([guild])
    print("New guild added.")


@client.event
async def on_guild_remove(guild):
    db.remove_guild(guild.id)
    print("Guild removed.")


@client.event
async def on_guild_channel_delete(channel):
    db.remove_channel(channel.guild.id, channel.id)
    print("Channel removed.")


@client.event
async def on_guild_channel_create(channel):
    db.add_channel(channel.guild.id, channel.id)
    print("Channel added.")


@client.event
async def on_ready():
    client.dm_queue = MessageQueue(client.loop)
    await tree.sync()
    db.add_guilds(client.guilds)
    db.add_channels(client.guilds)
    print("Guilds added and Commands synced.")


client.run(getenv("BOT_TOKEN"))
