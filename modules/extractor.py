from typing import List


def extract_all(message) -> List[str]:
    return normal_items(message.content) + embed_items(message.embeds)


def embed_items(embeds: list) -> list[str]:
    content = []
    for embed in embeds:
        embed = embed.to_dict()
        #  The only reason we remove backticks is to avoid discords fancy message thing: `hello`
        #  This is only to correct basE91 detections
        if "title" in (keys := embed.keys()):
            for word in embed["title"].split(" "):
                if word.startswith("`") and word.endswith("`"):
                    content.append(word[1:-1])
                content.append(word.replace("`", " "))
        if "description" in keys:
            for word in embed["description"].replace("\n", "").split(" "):
                if word.startswith("`") and word.endswith("`"):
                    content.append(word[1:-1])
                content.append(word.replace("`", " "))
        if "fields" in keys:
            for field in embed["fields"]:
                for word in field["name"].split(" "):
                    if word.startswith("`") and word.endswith("`"):
                        content.append(word[1:-1])
                    content.append(word.replace("`", " "))
                for word in field["value"].split(" "):
                    if word.startswith("`") and word.endswith("`"):
                        content.append(word[1:-1])
                    content.append(word.replace("`", " "))
    return content


def normal_items(content: str) -> list[str]:
    result = []
    for word in content.replace("\n", " ").split(" "):
        if word.startswith("`") and word.endswith("`"):
            result.append(word[1:-1])
        elif "`" in word:
            result.append(word)
        else:
            result.append(word.replace("`", " "))
    return result
