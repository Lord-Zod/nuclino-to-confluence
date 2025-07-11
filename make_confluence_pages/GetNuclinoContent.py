"""
Easy Wrapper for getting Nuclino page content
"""
import requests
from requests.auth import HTTPBasicAuth

from auth_creds import nuclino_creds


def get_nuclino_page_content(doc_id:str)->str:
    """

    :return:
    """
    headers = nuclino_creds.get_nuclino_auth_request()

    results = requests.get(
        f"https://api.nuclino.com/v0/items/{doc_id}",
        headers=headers
    )
    data = results.json()
    data = data.get('data').get('content')
    return data