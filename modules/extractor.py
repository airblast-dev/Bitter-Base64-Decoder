from typing import Generator
from itertools import chain


def extract_all(message) -> Generator:
    return chain(normal_items(message.content), embed_items(message.embeds))


def embed_items(embeds: list) -> Generator:
    for embed in embeds:
        embed = embed.to_dict()
        #  The only reason we remove backticks is to avoid discords fancy message thing: `hello`
        #  This is only to correct basE91 detections
        if "title" in (keys := embed.keys()):
            for word in embed["title"].split(" "):
                if word.startswith("`") and word.endswith("`"):
                    yield (word[1:-1])
                yield (word.replace("`", " "))
        if "description" in keys:
            for word in embed["description"].replace("\n", "").split(" "):
                if word.startswith("`") and word.endswith("`"):
                    yield (word[1:-1])
                yield (word.replace("`", " "))
        if "fields" in keys:
            for field in embed["fields"]:
                for word in field["name"].split(" "):
                    if word.startswith("`") and word.endswith("`"):
                        yield (word[1:-1])
                    yield (word.replace("`", " "))
                for word in field["value"].split(" "):
                    if word.startswith("`") and word.endswith("`"):
                        yield (word[1:-1])
                    yield (word.replace("`", " "))


def normal_items(content: str) -> Generator:
    for word in content.replace("\n", " ").split(" "):
        if word.startswith("`") and word.endswith("`"):
            yield (word[1:-1])
        elif "`" in word:
            yield (word)
        else:
            yield (word.replace("`", " "))
