class Emoji:
    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class Encodings:
    names = ["Base64", "basE91"]
    base64_desc = (
        "[Base64](https://en.wikipedia.org/wiki/Base64) is an encoding scheme that is used to represent binary data "
        + "(more specifically, a sequence of 8-bit bytes) in a sequence of 24 bits that can be represented by four 6-bit Base64 digits. "
        + 'You might ask whats with the equals sign "==" is doing there. The equals sign or signs are there to pad the data to 24 bits. '
        + "In other words they dont exactly carry any data. They are essentially there to protect the validity of the content still being 24 bits.\n"
        + "To manually decode any base64 content you can go [here](https://www.base64decode.org)."
    )

    base91_desc = (
        "[basE91](https://en.everybodywiki.com/BasE91) is an encoding scheme that is used to represent binary data."
        + " It divides a binary data stream into 13-bit packets which are then encoded in 2 ASCII characters."
        + " Compared to base64 it is 1/3 more efficient when it comes to size. However with the smaller size"
        + " also comes a slower encoding and decoding algorithm.\n"
        + "basE91 encryption includes the backtick (\`) character which discord uses to decorate messages like `this`."
        + "To manually decode any basE91 content you can go [here](https://www.dcode.fr/base-91-encoding)."
    )
    

    # For the defaults True means enabled, False means disabled and None means that it cant be enabled for any reason.
    complete = {
        "Base64": {
            "description": base64_desc,
            "default": {"text": False, "urls": True, "magnets": False},
            "link": "https://www.dcode.fr/base-91-encoding"
        },
        "basE91": {
            "description": base91_desc,
            "default": {"text": False, "urls": False, "magnets": False},
            "link": "https://www.base64decode.org"
        },
    }
