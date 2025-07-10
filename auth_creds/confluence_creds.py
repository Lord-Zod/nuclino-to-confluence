"""
Get Confluence API Credentials
"""
import configparser

def get_confluence_auth_creds(path_to_creds:str='.password_file_ini')->dict:
    """

    :return:
    """
    config = configparser.ConfigParser()
    config.read(path_to_creds)

    OUT = {
        'user': config['confluence']['user'],
        'key': config['confluence']['key'],
    }

    return OUT