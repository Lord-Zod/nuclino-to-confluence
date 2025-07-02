"""
Creates a yaml file representing the entity relationships of docs and collections
"""
## PYTHON IMPORTS
import configparser
from datetime import datetime, timedelta
from pprint import pprint
import requests
import yaml

## LOCAL IMPORTS
from auth_creds import nuclino_creds


class DocUser:
    """

    """
    def __init__(self, user_id:str, user_name_first:str, user_name_last:str, email:str):
        self.user_id = user_id
        self.user_name_first = user_name_first
        self.user_name_last = user_name_last
        self.email = email

    def __eq__(self, other):
        return (self.user_id == other.user_id)

    def __lt__(self, other):
        return (f'{self.user_name_first}-{self.user_name_last}' < f'{other.user_name_first}-{other.user_name_last}')


class DocEntity:
    """

    """
    def __init__(self, name: str, id: str, type:str, childIDs:list):
        """

        :param name:
        :param id:
        :param childIDs:
        """
        self.name = name
        self.id = id
        self.childIDs = childIDs
        self.type = type
        self.workspace:DocEntity = None
        self.parent:DocEntity = None
        self.children:list = []
        self.created_date:datetime = None
        self.updated_date:datetime = None
        self.created_by:DocUser = None
        self.updated_by:DocUser = None
        self.age:timedelta = None
        self.url:str = None

class DocEntityTree:
    """

    """
    def __init__(self):
        self.docs = []

class UserList:
    def __init__(self):
        self.users = {}

    def get_user(self, user_id:str)->DocUser:
        """

        :param user_id:
        :return:
        """
        if user_id in self.users.keys():
            return self.users[user_id]
        else:
            headers = nuclino_creds.get_nuclino_auth_request()
            results = requests.get(
                f'https://api.nuclino.com/v0/users/{user_id}',
                headers=headers
            ).json().get('data')
            tmp = DocUser(user_id, user_name_first=results.get('firstName'), user_name_last=results.get('lastName'), email=results.get('email'))
            self.users[user_id] = tmp
            return tmp


def get_settings()->dict:
    """

    :return:
    """
    OUT = {}
    configs = configparser.ConfigParser()
    configs.read("settings.config")

    # Convert to a dictionary
    OUT = {section: dict(configs.items(section)) for section in configs.sections()}
    return OUT


def get_workspaces(allow_list:list, users:UserList)->dict:
    """

    :return:
    """
    OUT = DocEntityTree()
    headers = nuclino_creds.get_nuclino_auth_request()

    results = requests.get(
        "https://api.nuclino.com/v0/workspaces",
        headers=headers
    )
    data = results.json().get('data').get('results')

    for doc in data:
        if (doc['name'] in allow_list):
            tmp = DocEntity(doc['name'], doc['id'], 'Workspace', doc['childIds'])
            tmp.type = 'Workspace'
            tmp.created_date = datetime.strptime(doc['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            tmp.created_by = users.get_user(doc['createdUserId'])
            OUT.docs.append(tmp)
    return OUT

def get_children(entity:DocEntity):
    """

    :param entity:
    :return:
    """

def get_nuclino_entity_tree()->dict:
    """

    :return:
    """
    OUT = {}
    users = UserList()
    headers = nuclino_creds.get_nuclino_auth_request()
    params = {
        'workspaceId': None
    }
    allowed_workspaces = get_settings()['workspaces']['allowlist'].split(',')
    workspaces = get_workspaces(allowed_workspaces, users)

    for workspace in workspaces.docs:
        response = requests.get(
            'https://api.nuclino.com/v0/items',
            params={'workspaceId': workspace.id},
            headers=headers
        )
        docs = response.json().get('data').get('results')
        for doc in docs:
            tmp = DocEntity(doc['title'], doc['id'], 'Document', doc.get('childIds'))
            tmp.created_date = datetime.strptime(doc['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            tmp.updated_date = datetime.strptime(doc['lastUpdatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            tmp.created_by = users.get_user(doc['createdUserId'])
            tmp.updated_by = users.get_user(doc['lastUpdatedUserId'])
            tmp.workspace = workspace
            tmp.parent = workspace
            tmp.url = doc['url']
    return OUT


if __name__ == '__main__':
    results = get_nuclino_entity_tree()