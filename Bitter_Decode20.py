import discord
import base64
from datetime import datetime
from validators import domain as vdom

rezi_support = input(f"Type 'yes' to enable Rezi Bot support: ").lower()
cove_bot_support = input(f"Type 'yes' to enable Cove Bot support: ").lower()
while True:
    scache_limit = input(
        f"Enter a number for the soft cache limit. This limit is what the bot will try to adhere to. Leave blank for default value. (Default is 1800): "
    )
    if scache_limit == "":
        scache_limit = 1800
        break
    try:
        int(scache_limit)
        break
    except:
        continue
if int(scache_limit) < 2:
    scache_limit = 2
scache_limit = int(scache_limit)
while True:
    hcache_limit = input(
        f"Enter a number for hard cache limit. This limit is what will be adhered to at all times. Leave blank for default value. (Default is 2000) :"
    )
    if hcache_limit == "":
        hcache_limit = 2000
        break
    try:
        int(hcache_limit)
        break
    except:
        continue
hcache_limit = int(hcache_limit)
if int(hcache_limit) < 2:
    hcache_limit = 2

if scache_limit >= hcache_limit:
    hcache_limit = scache_limit + 1

while True:
    logging = input(
        f"Enter 'true' to enable logging. This will only log the decoded string and time/date. Any other response will keep logging disabled: "
    ).lower()
    break


hcache_limit = int(hcache_limit)
now = str(datetime.now())
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
per_reaction = dict()


def b64dec(x):

    x = base64.b64decode(x + "==")
    x = x.decode("ascii")
    return x


def b64enc(x):
    x = x.encode("ascii")
    x = base64.b64encode(x)
    x = x.decode("ascii")
    return x


@client.event
async def on_ready():
    global client
    print(f"We have logged in as {client.user}.")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=f"b!help in a channel"
        )
    )


@client.event
async def on_message(message):
    count = 1
    emoji = "1️⃣"
    global per_reaction
    if len(message.embeds) == 0:
        for line in message.content.split():
            try:
                if line.replace("=", "").replace("`", "", 6) == b64enc(
                    b64dec(line.replace("`", "", 6))
                ).replace("=", ""):
                    line = line.replace("`", "", 6)
            except:
                pass
            try:
                if line.replace("=", "") == b64enc(b64dec(line)).replace("=", ""):
                    emoji = emoji[1:]
                    emoji = str(count) + emoji
                    if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                        await message.add_reaction(emoji)
                        if count == 1:
                            per_reaction[message.id] = {}
                        per_reaction[message.id][count] = b64dec(line)
                        per_reaction[message.id]["usage"] = 0
                        count += 1
            except:
                pass
            if message.content == "b!help":
                help_embed = discord.Embed(
                    title=f"This bot reacts to messages with a base64 encoded string and each reaction represents a base64 "
                    "string. Click on one of the reactions to get the decoded text.\nFor an example click the reaction "
                    "bellow."
                )
                await message.channel.send(embed=help_embed)
                await message.channel.send(
                    "``aHR0cHM6Ly93d3cueW91dHViZS5jb20v and aGVyZSBpcyBhbm90aGVyIGJhc2U2NCA6Lik``"
                )
    try:
        if (
            rezi_support == "yes" and str(message.author) == "Rezi#8393"
        ):  # This part is so the bot works well with Rezi Bot, to enable it
            emoji = "1️⃣"  # just type in 'yes' on startup.
            embeds = message.embeds
            count = 1
            for embed in embeds:
                embed_dict = embed.to_dict()
                for line in embed_dict["fields"]:
                    line = line["value"]
                    try:
                        if line.replace("=", "") == b64enc(b64dec(line)).replace(
                            "=", ""
                        ):
                            emoji = emoji[1:]
                            emoji = str(count) + emoji
                            if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                                if count == 1:
                                    per_reaction[message.id] = {}
                                if b64dec(line).startswith("http://") or b64dec(
                                    line
                                ).startswith("https://"):
                                    per_reaction[message.id][count] = b64dec(line)
                                else:
                                    per_reaction[message.id][
                                        count
                                    ] = "http://" + b64dec(line)
                                per_reaction[message.id]["usage"] = 0
                                count += 1
                                await message.add_reaction(emoji)
                    except:
                        pass
    except:
        pass
    try:
        if (
            cove_bot_support == "yes" and str(message.author) == "CoveBot#6047"
        ):  # This part is so the bot works well with Rezi Bot, to enable it
            emoji = "1️⃣"  # just type in 'yes' on startup.
            embeds = message.embeds
            count = 1
            for embed in embeds:
                embed_dict = embed.to_dict()
                for line in embed_dict["description"].split():
                    try:
                        if line.replace("=", "") == b64enc(b64dec(line)).replace(
                            "=", ""
                        ):
                            emoji = emoji[1:]
                            emoji = str(count) + emoji
                            if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                                if count == 1:
                                    per_reaction[message.id] = {}
                                if b64dec(line).startswith("http://") or b64dec(
                                    line
                                ).startswith("https://"):
                                    per_reaction[message.id][count] = b64dec(line)
                                else:
                                    per_reaction[message.id][
                                        count
                                    ] = "http://" + b64dec(line)
                                per_reaction[message.id]["usage"] = 0
                                count += 1
                                await message.add_reaction(emoji)
                    except:
                        pass
    except:
        pass


@client.event
async def on_raw_reaction_add(payload):
    global per_reaction
    print(per_reaction)
    if payload.member == client.user:
        return
    try:
        a = per_reaction[payload.message_id]
        try:
            x = a["usage"]
        except:
            del per_reaction[payload.message_id]
            return
    except:
        pass
    if (
        len(per_reaction) >= scache_limit
    ):             # Once the cache is full this will run. This part removes all message's from cache that have lower
        total = 0  # than average usage. Messages that aren't deleted from the cache gets their usage value set to 0.
        count = 0  # This is so only active messages are cached.
        del_list = list()
        for item in per_reaction:
            try:
                total = per_reaction[item]["usage"] + total
            except:
                del_list.append(item)
            count += 1
        for item in del_list:
            del per_reaction[item]
        del_list = list()
        avg = total / count
        for item in per_reaction:
            if per_reaction[item]["usage"] <= avg:
                del_list.append(item)
            per_reaction[item]["usage"] = 0
        for item in del_list:
            del per_reaction[item]
        print("Auto clean complete.")
    if (
        len(per_reaction) >= hcache_limit
    ):             # If for some reason this limit is meet (such as the 'usage' key having the same value across the board) this will
        count = 0  # delete half of set cache hard limit. (by default hard limit is 2000, so 1000 will get deleted.)
        for item in per_reaction:
            del_list.append(item)
            count += 1
            if count >= 2000:
                break
        for item in del_list:
            del per_reaction[item]
            count += 1
            if count >= hcache_limit // 2:
                break
        print("Force clean complete.")
    try:
        int(payload.emoji.name[0])
    except:
        return
    channel = await client.fetch_channel(payload.channel_id)
    if (
        payload.message_id in per_reaction and payload.member != client.user
    ):  # This area is for normal user sent messages, this is for messages that are already in the cache.
        print("Response is in cache.")
        decoded_embed = discord.Embed(
            title="Bitter decoded this to:",
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        await payload.member.send(embed=decoded_embed)
        if logging == "true":
            with open("auto_log.txt", "a") as file:
                file.write(
                    f"{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n"
                )
        per_reaction[payload.message_id]["usage"] += 1
        return
    message = await channel.fetch_message(payload.message_id)
    if (
        rezi_support == "yes"
        and payload.message_id not in per_reaction
        and str(message.author) == "Rezi#8393"
    ):                           # This whole part is so the bot works well with Rezi Bot, to enable it
        embeds = message.embeds  # just type in 'yes' on startup.
        count = 1
        per_reaction[payload.message_id] = dict()
        for embed in embeds:
            embed_dict = embed.to_dict()
            for line in embed_dict["fields"]:
                line = line["value"]
                if line == b64enc(b64dec(line)):
                    emoji = str(count) + "️⃣"
                    if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                        await message.add_reaction(
                            emoji
                        )  # Rezi Bot usually doesn't store links without the "https://" part ,so they aren't clickable in DM's.
                        if b64dec(line).startswith("https://") or b64dec(
                            line
                        ).startswith("http://"):
                            per_reaction[payload.message_id][
                                count
                            ] = "http://" + b64dec(line)
                        else:
                            per_reaction[payload.message_id][count] = b64dec(line)
                        count += 1
            decoded_embed = discord.Embed(
                title="Bitter decoded this to:",
                description=per_reaction[payload.message_id][
                    int(payload.emoji.name[0])
                ],
                color=0x444444,
            )
            await payload.member.send(embed=decoded_embed)
            per_reaction[payload.message_id]["usage"] = 1
            return
    if (
        cove_bot_support == "yes"
        and payload.message_id not in per_reaction
        and str(message.author) == "CoveBot#6047"
    ):
        embeds = message.embeds  # just type in 'yes' on startup.
        count = 1
        per_reaction[payload.message_id] = dict()
        for embed in embeds:
            embed_dict = embed.to_dict()
            for line in embed_dict["description"].split():
                if line == b64enc(b64dec(line)):
                    emoji = str(count) + "️⃣"
                    if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                        await message.add_reaction(
                            emoji
                        )  # Rezi Bot usually doesn't store links without the "https://" part ,so they aren't clickable in DM's.
                        if b64dec(line).startswith("https://") or b64dec(
                            line
                        ).startswith("http://"):
                            per_reaction[payload.message_id][
                                count
                            ] = "http://" + b64dec(line)
                        else:
                            per_reaction[payload.message_id][count] = b64dec(line)
                        count += 1
        decoded_embed = discord.Embed(
            title="Bitter decoded this to:",
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        await payload.member.send(embed=decoded_embed)
        per_reaction[payload.message_id]["usage"] = 1
        return
    if (
        payload.member != client.user and str(message.author) != "Rezi#8393"
    ):  # This part is to read old messages that got the reaction and stores the message
        print("Response is not in cache.")  # contents into the cache.
        message = await channel.fetch_message(payload.message_id)
        count = 1
        per_reaction[payload.message_id] = dict()
        for line in message.content.split():
            try:
                if line.replace("=", "").replace("`", "", 6) == b64enc(
                    b64dec(line.replace("`", "", 6))
                ).replace("=", ""):
                    line = line.replace("`", "", 6)
            except:
                pass
            try:
                if len(b64dec(line)) > 4 and vdom(b64dec(line)) or vurl(b64dec(line)) :
                    per_reaction[payload.message_id][count] = b64dec(line)
                    count += 1
                    if logging == "true":
                        with open("auto_log.txt", "a") as file:
                            file.write(
                                f"{per_reaction[payload.message_id][int(payload.emoji.name[0])]}:{now}\n"
                            )
            except:
                pass
        decoded_embed = discord.Embed(
            title="Bitter decoded this to:",
            description=per_reaction[payload.message_id][int(payload.emoji.name[0])],
            color=0x444444,
        )
        await payload.member.send(embed=decoded_embed)
        per_reaction[payload.message_id]["usage"] = 1
        return


client.run("Your Token")
