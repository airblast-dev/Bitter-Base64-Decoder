import pymongo
from modules.statics import Encodings
from typing import List, Sequence
from modules.templates import Settings, Search_Result
from discord import TextChannel, Thread

settings = {
    name: Encodings.complete[name]["default"] for name in Encodings.names
    }

class BitterDB:
    def __init__(self, cn_str: str, db_name: str):
        db_client = pymongo.MongoClient(cn_str)
        self.bitter_db = db_client[db_name]
        self.bitter_db["guilds"].create_index([("guild_id", pymongo.ASCENDING)])
        self.bitter_db["channels"].create_index([("channel_id", pymongo.ASCENDING)], unique=True)
        self.bitter_db["messages"].create_index(
            [
                ("guild_id", pymongo.ASCENDING), 
                ("channel_id", pymongo.ASCENDING), 
                ("message_id", pymongo.ASCENDING), 
                ("content", pymongo.ASCENDING)
            ], 
            unique=True
        )

    def add_guilds(self, guilds: Sequence) -> None:
        old_id = set(self.bitter_db["guilds"].distinct("guild_id"))
        #  We compare all guilds joined to the ones that are already stored and then only insert new guilds.
        new_docs = [{"guild_id": guild.id, "name": guild.name, "settings": settings} for guild in guilds if guild.id not in old_id]
        if len(new_docs) == 0:
            return
        self.bitter_db["guilds"].insert_many(new_docs).inserted_ids
 
    def add_guild(self, guild) -> None:
        self.bitter_db["guilds"].insert_one({"guild_id": guild.id, "name": guild.name, "settings": settings})

    def remove_guild(self, guild_id) -> None:
        self.bitter_db["guilds"].delete_one({"guild_id": guild.id})

    def get_guild_settings(self, guild_id) -> Settings:
        guild_setting = self.bitter_db["guilds"].find_one({"guild_id": guild_id})
        if guild_setting is None:
            return {key:Encodings.complete[key]["default"] for key in Encodings.complete.keys()}
        return guild_setting["settings"]

    def edit_guild_settings(
        self, guild_id, encoding: str, detection: str, new: bool
    ) -> Settings:       
        return self.bitter_db["guilds"].find_one_and_update(
            {"guild_id": guild_id},
            {"$set": {f"settings.{encoding}.{detection}": new}},
            {"settings": 1},
            return_document=True,
        )["settings"]

    def add_channels(self, guilds) -> None:
        old_id = set(self.bitter_db["channels"].distinct("channel_id"))
        for guild in guilds:
            channels = [{"channel_id": channel.id, "name": channel.name, "guild_id": channel.guild.id} for channel in guild.text_channels if channel.id not in old_id]
            threads = [{"channel_id": thread.id, "name": thread.name, "guild_id": thread.guild.id} for thread in guild.threads if thread.id not in old_id]
            if len(channels + threads) == 0:
                continue
            self.bitter_db["channels"].insert_many(channels + threads)

    def remove_channel(self, guild_id, channel_id) -> None:
        self.bitter_db["channels"].delete_one({"channel_id": channel_id})
        self.bitter_db["messages"].delete_many({"channel_id": channel_id})

    def add_channel(self, guild_id, channel_id) -> None:
        self.bitter_db["channels"].insert_one({"guild_id": guild_id, "channel_id": channel_id})

    def insert_content(
        self, guild_id, channel_id, message_id, content: List[str], jump_url: str
    ) -> None:
        # This replaces the older message id because in a majority of cases if a piece of content is duplicate 
        # it means the older one will not be used as much or might not be used at all.
        # In the case the older message is reacted it will replace the newer one. 
        # This avoids constantly storing the same content but for different message id's.
        # It will still insert a new message in case duplicate content isnt found for that channel.
        # Another alternative would be to store message id's in an array but that would make it unbounded and hard to clear.
        self.bitter_db["messages"].update_one(
            {
                "guild_id": guild_id,
                "channel_id": channel_id, 
                "content": content
            },
            {
                "$set": {
                    "jump_url": jump_url,
                    "message_id": message_id
                },
                "$setOnInsert": {
                    "channel_id": channel_id,
                    "content": content,
                    "guild_id": guild_id
                }
            },
            upsert=True
        )

    def find_content(self, guild_id, channel_id, message_id) -> Search_Result:
        document = self.bitter_db["messages"].find_one(
            {
                "guild_id": guild_id,
                "channel_id": channel_id, 
                "message_id": message_id
            }
        )
        if document is None:
            return None
        return {
            "content": document["content"],
            "jump_url": document["jump_url"],
        }

    def edit_content(self, guild_id, channel_id, message_id, content: List[str], jump_url: str) -> None:
        result = self.bitter_db["messages"].update_one(
            {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "message_id": message_id,
            },
            {
                "$set":{
                    "content": content,
                    "jump_url": jump_url
                }
            }
        )
        if result.modified_count == 0:
            return False
        return True

    def delete_content(self, guild_id, channel_id, message_id, content: List[str]) -> None:
        document = self.bitter_db["messages"].delete_one(
            {
                "guild_id": guild_id,
                "channel_id": channel_id, 
                "message_id": message_id
            }
        )

