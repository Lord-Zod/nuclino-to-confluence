"""# Read Doc YAML
# For Each Doc
# ... Create Doc in Space
# ... Add Table with Archival Info
# ... Add title"""
# PYTHON IMPORTS
from datetime import datetime
import logging
import os
from pprint import pprint, pformat
import yaml

from make_confluence_pages import PageHandler, DocUser, DocEntity, DocEntityTree, UserList
from get_nuclino_entity_tree import get_settings

logger = logging.getLogger(__name__)
loghandle = logging.FileHandler(os.path.normpath(os.path.join(os.getcwd(), 'create_confluence_pages.log')))
loghandle.setLevel(logging.DEBUG)
logger.addHandler(loghandle)

TESTING_SETTINGS = {
    'make_space_folder': False,
    'make_content': False,
    'make_page': False,
    'add_tags': False,
    'assign_parents': False,
    'migrate_images': True,
    'migration_testing_count': None,
    'use_parenting_mockup': True,
}

def make_docs():
    """

    :return:
    """
    logger.info(
        f'''-------------
Beginning new run
{datetime.now().strftime("%Y%m%d-%H:%M:%S")}'''
    )

    data = {}
    datafile = 'nuclino_entity_tree_parent_testing.yaml' if TESTING_SETTINGS['use_parenting_mockup'] else 'nuclino_entity_tree.yaml'
    with open(datafile, 'r') as docs_file:
        data = yaml.safe_load(docs_file)

    # Create parent import folder
    if TESTING_SETTINGS['make_space_folder']:
        parent_folder_name = 'Nuclino Docs Import'
        folder_results = PageHandler.PageHandler.create_confluence_folder(parent_folder_name)
        if not folder_results['status']:
            logger.warning(pformat(folder_results))
            return False

    page_handler = PageHandler.PageHandler()

    # Create Nuclino Pages in Confluence
    # countdown = len(data)
    countdown = len(data) if not TESTING_SETTINGS['migration_testing_count'] else TESTING_SETTINGS['migration_testing_count']
    for doc in data:
        # A Testing Failsafe
        # Example: set "countdown" to a smaller number when testing initial pipeline
        logger.info(f'Countdown: {countdown}')
        if countdown <= 0:
            break

        # Create the doc body content
        if TESTING_SETTINGS['make_content']:
            content_results = page_handler.create_page_content(data[doc], logger)
            logger.info(f'''Results of creating page content:
{pformat(content_results)}''')
            if not content_results['status']:
                logger.warning(f'Creating page content failed. Decrementing countdown. Continuing to next doc')
                countdown -= 1
                continue

        # Create the page in Confluence
        if TESTING_SETTINGS['make_page']:
            create_results = page_handler.create_confluence_page(parent_folder=folder_results['folder_id'])
            if not create_results['status']:
                logger.warning('Creating Confluence Page failed')
                logger.warning(f'{pformat(create_results)}')

        # Tag the page for later ease of finding by nuclino ID
        if TESTING_SETTINGS['add_tags'] and TESTING_SETTINGS['make_page']:
            tag_results = page_handler.tag_nuclino_page_id()
            pprint(tag_results)
            if not tag_results['status']:
                logger.warning(f'Failed to tag page: {pformat(tag_results)}')

        logger.info('Decrementing Countdown')
        countdown -= 1

    # Setting Parent Doc Relationships
    if TESTING_SETTINGS['assign_parents']:
        logger.info(f'Beginning Parent Relationship Assignment')
        for doc in data:
            result = page_handler.set_doc_parent(data[doc], logger)
            logger.info(f'{result} - {pformat(data[doc])}')

    if TESTING_SETTINGS['migrate_images']:
        logger.info('Beginning Image Migration')
        for doc in data:
            result = page_handler.download_image_from_nuclino_page(data[doc], logger, get_settings())
            logger.info(f'{result}')
    print('end')

if __name__ == '__main__':
    make_docs()