"""# Read Doc YAML
# For Each Doc
# ... Create Doc in Space
# ... Add Table with Archival Info
# ... Add title"""
# PYTHON IMPORTS
import yaml

from make_confluence_pages import PageHandler, DocUser, DocEntity, DocEntityTree, UserList



def make_docs():
    """

    :return:
    """
    data = {}
    with open('nuclino_entity_tree.yaml', 'r') as docs_file:
        data = yaml.safe_load(docs_file)

    page_handler = PageHandler()

    countdown = 3
    for doc in data:
        if countdown <= 0:
            break

        page_handler.


