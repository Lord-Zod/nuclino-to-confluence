"""
Creates a yaml file representing the entity relationships of docs and collections
"""
## PYTHON IMPORTS
from pprint import pprint
import requests
import yaml

## LOCAL IMPORTS
from auth_creds import nuclino_creds



def get_workspaces()->dict:
    """

    :return:
    """
    OUT = {}
    headers, params = nuclino_creds.get_nuclino_auth_request()

    results = requests.get(
        "https://api.nuclino.com/v0/workspaces",
        headers=headers
    )
    OUT = results.json()
    pprint(OUT)
    return OUT

def get_nuclino_entity_tree()->dict:
    """

    :return:
    """
    OUT = {}
    headers, params = nuclino_creds.get_nuclino_auth_request()

    response = requests.get('https://api.nuclino.com/v0/items', params=params, headers=headers)
    return OUT


if __name__ == '__main__':
    results = get_workspaces()