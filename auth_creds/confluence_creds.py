"""
Get Confluence API Credentials
"""
import configparser
import json
from pprint import pprint, pformat
import requests
from requests.auth import HTTPBasicAuth
import sys


def get_confluence_auth_creds(path_to_creds:str='.password_file_ini')->dict:
    """

    :return:
    """
    config = configparser.ConfigParser()
    config.read(path_to_creds)


    OUT = {
        'user': config['confluence']['user'],
        'key': config['confluence']['key'],
        'domain': config['confluence']['domain'],
        'spaceID': config['confluence']['spaceID'],
    }

    return OUT

def get_confluence_space_id_by_key(space_key:str="")->str:
    """

    :param space_key:
    :return:
    """

    confluence_data = get_confluence_auth_creds()
    auth = HTTPBasicAuth(
        confluence_data.get('user'),
        confluence_data.get('key')
    )

    url = f"https://{confluence_data.get('domain')}/wiki/api/v2/spaces"
    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    if response.status_code != 200:
        return False

    spaces = response.json().get('results')
    pprint(spaces)
    spaceID = [x.get('id') for x in spaces if x.get('key') == space_key]
    pprint(spaceID)

    return spaceID


if __name__ == "__main__":
    print(get_confluence_space_id_by_key(sys.argv[0]))