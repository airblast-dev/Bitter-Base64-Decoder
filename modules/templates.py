from typing import List, TypedDict, Union

class Options(TypedDict):
    text: Union[bool, None]
    urls: Union[bool, None]
    magnets: Union[bool, None]

class Settings(TypedDict):
    base64: Options
    basE91: Options
    
class Search_Result(TypedDict):
    content: List[str]
    jump_url: str