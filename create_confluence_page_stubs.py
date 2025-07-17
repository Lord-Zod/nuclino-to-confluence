"""# Read Doc YAML
# For Each Doc
# ... Create Doc in Space
# ... Add Table with Archival Info
# ... Add title"""
# PYTHON IMPORTS
from pprint import pprint
import yaml

from make_confluence_pages import PageHandler, DocUser, DocEntity, DocEntityTree, UserList



def make_docs():
    """

    :return:
    """
    data = {}
    with open('nuclino_entity_tree.yaml', 'r') as docs_file:
        data = yaml.safe_load(docs_file)

    # Create parent import folder
    parent_folder_name = 'Nuclino Docs Import'
    folder_results = PageHandler.PageHandler.create_confluence_folder(parent_folder_name)
    if not folder_results['status']:
        pprint(folder_results)
        return False

    page_handler = PageHandler.PageHandler()

    # Create Nuclino Pages in Confluence
    countdown = len(data)
    for doc in data:
        # A Testing Failsafe
        # Example: set "countdown" to a smaller number when testing initial pipeline
        if countdown <= 0:
            break

        # Create the doc body content
        page_handler.create_page_content(data[doc])

        # Create the page in Confluence
        if not page_handler.create_confluence_page(parent_folder=folder_results['folder_id']):
            return False
        countdown -= 1

        # Tag the page for later ease of finding by nuclino ID
        results = page_handler.tag_nuclino_page_id()
        pprint(results)
        if not results['status']:
            return False

    # Setting Parent Doc Relationships
    for doc in data:
        pass


    print('end')

if __name__ == '__main__':
    make_docs()