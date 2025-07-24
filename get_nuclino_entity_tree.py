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
            tmp.childIDs = doc['childIds']
            tmp.created_date = datetime.strptime(doc['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            tmp.created_by = users.get_user(doc['createdUserId'])
            OUT.add_doc(tmp)
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
        doc_list.add_doc(workspaces.docs[workspace])
        limit_size = 100
        load_size = 100
        last_id = None
        while load_size == limit_size:

            response = requests.get(
                'https://api.nuclino.com/v0/items',
                params={
                    'workspaceId': workspace,
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
                # doc_list.docs.append(tmp)
                doc_list.add_doc(tmp)

    doc_list.define_parents()
    return True
    # return OUT


if __name__ == '__main__':
    results = get_nuclino_entity_tree()
    print(doc_list.print_all_docs())
    with open('nuclino_entity_tree.yaml', 'w') as outfile:
        outfile.write(doc_list.print_all_docs())
    print('end')