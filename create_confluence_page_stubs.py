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
from auth_creds.confluence_creds import get_confluence_auth_creds

logger = logging.getLogger(__name__)
log_name = f'create_confluence_pages_{get_confluence_auth_creds().get("domain")}_{get_confluence_auth_creds().get("spaceID")}_{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.log'
loghandle = logging.FileHandler(os.path.normpath(os.path.join(os.getcwd(), log_name)))
loghandle.setLevel(logging.DEBUG)
logger.addHandler(loghandle)

TESTING_SETTINGS = {
    'make_space_folder': True,
    'make_content': True,
    'make_page': True,
    'add_tags': True,
    'assign_parents': True,
    'migrate_images': True,
    'attach_images': True,
    'link_images': True,
    'migration_testing_count': None,
    'use_parenting_mockup': False,
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
        parent_folder_name = 'Nuclino_Imports'
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
            logger.info(f'Preparing to migrate attachments for page: {data[doc].get("name")} @ {data[doc].get("url")}')
            file_download_result = page_handler.download_image_from_nuclino_page(data[doc], logger, get_settings())
            logger.info(f'{file_download_result}')
            if not file_download_result['status']:
                logger.error(file_download_result['msg'])
                return False

            confluence_page_id_results = page_handler.get_confluence_page_id(data[doc], logger)
            if not confluence_page_id_results['status']:
                logger.error('Failed to get confluence page ID')
                return False

            confluence_page_id = confluence_page_id_results['confluence_page_id']

            # Move to Confluence
            text_replacements = []
            did_text_replacement = False
            for file_download in file_download_result['files']:
                did_text_replacement = True

                already_attached = False
                if TESTING_SETTINGS['attach_images']:
                    confluence_attach_results = page_handler.attach_file_to_confluence_page_object(
                        data[doc],
                        file_download,
                        confluence_page_id,
                        logger
                    )
                    already_attached = confluence_attach_results['already_attached']
                    if not confluence_attach_results['status']:
                        logger.error(confluence_attach_results['msg'])
                        return False

                if TESTING_SETTINGS['link_images'] and not already_attached:
                    confluence_replacement_results = page_handler.get_confluence_page_attachment_replacements(
                        data[doc],
                        file_download,
                        confluence_page_id,
                        logger
                    )
                    if not confluence_replacement_results['status']:
                        logger.error(f"ERROR::{confluence_replacement_results['msg']}")
                        # return False
                    else:
                        text_replacements.append(confluence_replacement_results['replacement'])

            if len(text_replacements) > 0:
                body = text_replacements[0]['body']
                version = text_replacements[0]['version']
                title = text_replacements[0]['title']
                for item in text_replacements:
                    body = body.replace(
                        item['before'],
                        item['after']
                    )
                    version = item['version']
                update_results = page_handler.update_confluence_page_body(
                    confluence_page_id,
                    body,
                    version,
                    title,
                    logger
                )

                if not update_results['status']:
                    logger.error(update_results['msg'])
                    return False
                else:
                    logger.info(update_results['msg'])
            elif did_text_replacement and len(text_replacements) == 0:
                logger.warning('WARNING: Replacement searches FAILED')
            else:
                logger.info(f'No Replacement Searches for Confluence page: {confluence_page_id}')
    print('end')

if __name__ == '__main__':
    make_docs()