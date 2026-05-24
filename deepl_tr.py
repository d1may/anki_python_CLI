import os
import deepl
from anki.ui import Palette

def deepl_translate(text: str):
    try:
        auth_key = os.getenv("DEEPL_API_KEY")
        if not auth_key:
            return(f"{Palette.ERROR}DEEPL_API_KEY is not set")
        deepl_client = deepl.DeepLClient(auth_key)
        result = deepl_client.translate_text(f"{text}", target_lang="RU")
        return result.text
    except Exception as e:
        return (f"{Palette.ERROR}Error: {e}")