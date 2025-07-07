"""
Get Confluence API Credentials
"""
import configparser

def get_confluence_auth_creds()->dict:
    """

    :return:
    """
    config = configparser.ConfigParser()
    config.read('.password_file_ini')

    OUT = {
        'user': config['confluence']['user'],
        'key': config['confluence']['key'],
    }

    return OUT