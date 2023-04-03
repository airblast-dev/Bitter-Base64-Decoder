import validators
from typing import List

class Filters:
    def check_content(self, decoded: list, settings: dict) -> List[str]:
        filtered = []
        for item in decoded:
            if len(filtered) == 10:
                break
            if settings["text"] is True and self._is_text(item):
                filtered.append(item)
            elif settings["urls"] is True and self._is_url(item):
                filtered.append(item)
            elif settings["magnets"] is True and self._is_magnet(item):
                filtered.append(item)
        return filtered

    def _is_text(self, i: str) -> bool:
        if len(i) > 8:
            return True
        return False

    # is_url checks if content is an url or contains a url. So this allows things like sending a zip password or other information along with the message.
    def _is_url(self, i: str) -> bool:
        if validators.url(i) is True:
            return True
        for item in i.replace('\n', " ").split(" "):
            if validators.url(item) is True:
                return True
        return False

    def _is_magnet(self, i: str) -> bool:
        if i.startswith("magnet:?xt") or "magnet:?xt" in i:
            return True
        return False
