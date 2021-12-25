import json
from typing import Dict


def load_gif(filename: str) -> Dict:
    """Load json file with keyword and corresponding GIF link

    Args:
        filename (str): filename of a json file

    Returns:
        Dict: {keyword: link}
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_user(filename: str) -> Dict:
    """Load json file with Discord userid and corresponding wellcome message

    Args:
        filename (str): filename of a json file

    Returns:
        Dict: {userid: text, date}
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    processed_data = {}
    for key, value in data.items():
        processed_data[key] = {'text': value, 'date': None}
    return processed_data

def load_config(filename: str) -> str:
    """Load txt file with token and timezone

    Args:
        filename (str): filename of the config file

    Returns:
        str: token, timezone
    """
    with open(filename, 'r') as f:
        token = str.strip(f.readline().replace('token=', ''))
        timezone = str.strip(f.readline().replace('timezone=', ''))
        mode = str.strip(f.readline().replace('mode=', ''))
    return token, timezone, mode