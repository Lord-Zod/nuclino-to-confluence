"""

"""
import configparser
import requests



def get_nuclino_auth_creds()->dict:
    """
    Reads Nuclino authorization credentials file from .password_file_ini
    :return:
    """
    OUT = {}
    config = configparser.ConfigParser()
    config.read('.password_file_ini')
    OUT['user'] = config['nuclino']['user']
    OUT['key'] = config['nuclino']['key']
    OUT['site_id'] = config['nuclino']['site_id']
    return OUT

def get_nuclino_auth_request():
    """

    :return:
    """
    creds = get_nuclino_auth_creds()
    headers = {
        'Authorization': creds['key'],
    }

    params = {
        'workspaceId': creds['site_id']
    }
    return headers, params