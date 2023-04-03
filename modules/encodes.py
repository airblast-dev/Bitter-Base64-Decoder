import base64
import base91
from modules.filters import Filters
from typing import List, TypedDict
from modules.templates import Settings


def check_all(content: List[str], settings: Settings) -> list:
    result = []
    if any(settings["Base64"][key] for key in settings["Base64"].keys()):
        result += Base64.decode_list(content, settings["Base64"])
    if any(settings["basE91"][key] for key in settings["basE91"].keys()):
        result += BasE91.decode_list(content, settings["basE91"])
    return result[0:10]


def in_url_list(func):
    def inner(content: List[str], settings: Settings):
        result = func(content, settings)
        return [item for item in result if item in valid_urls]


# Any list decoding should use this decorator as it will filter results based on settings and limit the result for 10 items.
def list_control(func):
    def inner(content: List[str], settings: dict):
        decoded = func(content)
        return Filters().check_content(decoded, settings)

    return inner


# Any string decoding or encoding should return a string or None.
# Lists should return a list regardless of it being empty or not.
class Base64:
    def decode_str(content: str) -> str | None:
        try:
            return base64.urlsafe_b64decode((word + "==").encode()).decode()
        except Exception:
            return None

    @list_control
    def decode_list(content: List[str]) -> List[str]:
        result = []
        for word in content:
            try:
                result.append(base64.urlsafe_b64decode((word + "==").encode()).decode())
            except Exception:
                continue
        return result

    def encode_str(content: str) -> str | None:
        try:
            return base64.urlsafe_b64encode(content.encode()).decode()
        except Exception:
            return None

    def encode_list(content: List[str]) -> List[str]:
        result = []
        for word in content:
            try:
                result.append(base64.urlsafe_b64encode(word.encode())).decode()
            except Exception:
                continue
        return result


class BasE91:
    def decode_str(content: str) -> str | None:
        try:
            return base91.decode(content).decode()
        except Exception:
            return None

    @list_control
    def decode_list(content: List[str]) -> List[str]:
        result = []
        for word in content:
            try:
                result.append(base91.decode(word).decode())
            except Exception:
                continue
        return result

    def encode_str(content: str) -> str | None:
        try:
            return base91.encode(content.encode())
        except Exception:
            return None

    def encode_list(content: List[str]) -> List[str]:
        result = []
        for word in content:
            try:
                result.append(base91.encode(word.encode()))
            except Exception:
                continue
        return result


operations = {"Base64": Base64, "basE91": BasE91}
