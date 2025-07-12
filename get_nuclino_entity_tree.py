"""
Creates a yaml file representing the entity relationships of docs and collections
"""
## PYTHON IMPORTS
import configparser
from datetime import datetime, timedelta
from pprint import pprint, pformat
import requests
import yaml

## LOCAL IMPORTS
from auth_creds import nuclino_creds
from make_confluence_pages import *

#
# class UserList:
#     """
#     Stores all users as a lookup
#     If the user doesn't exist it will be queried from Nuclino
#         ,,, and added to the list
#     Else is will return the discovered user
#     """
#     def __init__(self):
#         self.users = {}
#
#     def get_user(self, user_id:str):
#         """
#
#         :param user_id:
#         :return:
#         """
#         if user_id in self.users.keys():
#             return self.users[user_id]
#         else:
#             headers = nuclino_creds.get_nuclino_auth_request()
#             results = requests.get(
#                 f'https://api.nuclino.com/v0/users/{user_id}',
#                 headers=headers
#             ).json().get('data')
#             tmp = DocUser(user_id, user_name_first=results.get('firstName'), user_name_last=results.get('lastName'), email=results.get('email'))
#             self.users[user_id] = tmp
#             return tmp
#
# class DocEntityTree:
#     """
#
#     """
#     def __init__(self):
#         self.docs = []
#
#     def get_all_children(self, nuclino_creds):
#         """
#
#         :return:
#         """
#         for doc in self.docs:
#             pass
#     def get_doc(self, doc_id:str):
#         """
#
#         :param doc_id:
#         :return:
#         """
#         if doc_id in self.docs.keys():
#             return self.docs[doc_id]
#         else:
#             headers = nuclino_creds.get_nuclino_auth_request()
#             results = requests.get(
#                 f'https://api.nuclino.com/v0/items/{doc_id}',
#                 headers=headers
#             ).json().get('data')
#             tmp = DocEntity(doc_id, user_name_first=results.get('firstName'), user_name_last=results.get('lastName'), email=results.get('email'))
#             self.docs[doc_id] = tmp
#             return tmp
#
#     def print_all_docs(self):
#         """
#
#         :return:
#         """
#         OUT = {}
#         for doc in self.docs:
#             OUT[doc.id] = doc.get_as_dict()
#         return yaml.dump(OUT, default_flow_style=False)
#
# user_list = UserList()
# doc_list = DocEntityTree()
#
# class DocUser:
#     """
#     Single user entity
#     """
#     def __init__(self, user_id:str, user_name_first:str, user_name_last:str, email:str):
#         self.user_id = user_id
#         self.user_name_first = user_name_first
#         self.user_name_last = user_name_last
#         self.email = email
#
#     def __eq__(self, other):
#         return (self.user_id == other.user_id)
#
#     def __lt__(self, other):
#         return (f'{self.user_name_first}-{self.user_name_last}' < f'{other.user_name_first}-{other.user_name_last}')
#
#     def __repr__(self):
#         return f'{self.user_name_first}-{self.user_name_last}-{self.email}'
#
#     def __str__(self):
#         return yaml.dump(self.get_as_dict(), default_flow_style=False)
#
#     def get_as_dict(self):
#         """
#
#         :return:
#         """
#         return {
#             'user_id': self.user_id,
#             'user_name_first': self.user_name_first,
#             'user_name_last': self.user_name_last,
#             'email': self.email
#         }
#
#
# class DocEntity:
#     """
#
#     """
#     def __init__(self, name: str, id: str, type:str):
#         """
#
#         :param name:
#         :param id:
#         :param childIDs:
#         """
#         self.name = name
#         self.id = id
#         self.childIDs = None
#         self.type = type
#         self.workspace:DocEntity = None
#         self.parent:DocEntity = None
#         self.children:list = []
#         self.created_date:datetime = None
#         self.updated_date:datetime = None
#         self.created_by:DocUser = None
#         self.updated_by:DocUser = None
#         self.age:timedelta = None
#         self.url:str = None
#
#     def __repr__(self):
#         return f'{self.workspace.name}-{self.name}-{self.type}-{self.updated_by.email}-{self.updated_date.strftime("%Y-%m-%d")}'
#
#     def __str__(self):
#         return yaml.dump(self.get_as_dict(), default_flow_style=False)
#
#     def get_as_dict(self):
#         """
#
#         :return:
#         """
#         return {
#             'name': self.name,
#             'id': self.id,
#             'type': self.type,
#             'childIDs': self.childIDs,
#             'workspace': self.workspace.name,
#             'parent': pformat(self.parent),
#             'children': pformat(self.children),
#             'created_date': self.created_date.strftime("%Y-%m-%d_%H:%M:%S") if self.created_date else None,
#             'updated_date': self.updated_date.strftime("%Y-%m-%d_%H:%M:%S") if self.updated_date else None,
#             'age': pformat(self.age),
#             'created_by': self.created_by.get_as_dict() if self.created_by else None,
#             'updated_by': self.updated_by.get_as_dict() if self.updated_by else None,
#             'url': self.url,
#         }
#
#     # def get_children_docs(self):
#     #     for child in self.childIDs:
#     #         results =
#     @classmethod
#     def from_full_object(cls, data):
#         """
#
#         :param data:
#         :return:
#         """
#
#         # name: str, id: str, type:str, childIDs:list
#         entity_type = 'Document'
#         if data.get('childIds'):
#             entity_type = 'Collection'
#         tmp = cls(
#             data.get('title'),
#             data.get('id'),
#             entity_type,
#         )
#         tmp.created_date = datetime.strptime(data.get('createdAt'), '%Y-%m-%dT%H:%M:%S.%fZ')
#         tmp.updated_date = datetime.strptime(data.get('lastUpdatedAt'), '%Y-%m-%dT%H:%M:%S.%fZ')
#         tmp.created_by = user_list.get_user(data.get('createdUserId'))
#         tmp.updated_by = user_list.get_user(data.get('lastUpdatedUserId'))
#         tmp.workspace = data.get('workspace')
#         tmp.age = tmp.updated_date - tmp.created_date
#         # tmp.parent = workspace
#         if entity_type == 'Collection':
#             tmp.childIDs = data.get('childIds')
#         tmp.url = data.get('url')
#         return tmp





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
            tmp = DocEntity(doc['name'], doc['id'], 'Workspace')
            tmp.type = 'Workspace'
            tmp.children = doc['childIds']
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
        limit_size = 100
        load_size = 100
        last_id = None
        while load_size == limit_size:

            response = requests.get(
                'https://api.nuclino.com/v0/items',
                params={
                    'workspaceId': workspace.id,
                    'limit': 100,
                    'after': last_id
                },
                headers=headers
            )
            tmp_data = response.json()
            docs = tmp_data.get('data').get('results')
            load_size = len(docs)
            last_id = docs[-1]['id']
            for doc in docs:
                doc['workspace'] = workspace
                tmp = DocEntity.from_full_object(doc)
                doc_list.docs.append(tmp)

    return True
    # return OUT


if __name__ == '__main__':
    results = get_nuclino_entity_tree()
    print(doc_list.print_all_docs())
    with open('nuclino_entity_tree.yaml', 'w') as outfile:
        outfile.write(doc_list.print_all_docs())
    print('end')