import os
import deepl

def deepl_translate(text: str):
    try:
        auth_key = os.getenv("DEEPL_API_KEY")
        if not auth_key:
            return("DEEPL_API_KEY is not set", Palette.ERROR)
        deepl_client = deepl.DeepLClient(auth_key)
        result = deepl_client.translate_text(f"{text}", target_lang="RU")
        return result.text
    except Exception as e:
        return (f"Error: {e}")