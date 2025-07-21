"""
Performs these tasks

1. Receive 1 DocEntity Object
2. Create Confluence Page Data
    a. Tags: self id, parent id
    b. body text
    c. Archival data as table
    d. Enforced Doc Template
    e. Keep accurate image references
3. Create Confluence Page in Desired Space
4. Ensure parent and child relationships are preserved
"""
import importlib
import markdown
import os
from pprint import pprint, pformat
import re
import sys
import requests
from requests.auth import HTTPBasicAuth
import json

from make_confluence_pages.MakeTemplateDoc import make_page_body
from make_confluence_pages.MakeArchivalHeader import make_table
from make_confluence_pages.GetNuclinoContent import get_nuclino_page_content
from auth_creds.confluence_creds import get_confluence_auth_creds


# Load the main module
load_import_from = os.path.join(os.path.abspath(os.getcwd()), 'import.py')
spec = importlib.util.spec_from_file_location('import.py', load_import_from)
mainModule = importlib.util.module_from_spec(spec)
sys.modules['import.py'] = mainModule
spec.loader.exec_module(mainModule)


class PageHandler:
    """

    """
    def __init__(self):
        self.page_content = None
        self.src_data = None
        self.confluence_doc_type = 'storage'
        self.confluence_page_data = None

    def _convert_nuclino_to_confluence_html(self, nuclino_page_data: str) -> str:
        """

        :param nuclino_page_data:
        :return:
        """
        OUT = markdown.markdown(nuclino_page_data,
                                extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code'])
        OUT = mainModule.convert_info_macros(OUT)
        OUT = mainModule.convert_comment_block(OUT)
        OUT = mainModule.convert_code_block(OUT)
        OUT = mainModule.process_refs(OUT)
        return OUT

    def tag_nuclino_page_id(self):
        """

        :return:
        """
        OUT = {}
        auth_creds = get_confluence_auth_creds()
        confluence_page_id = self.confluence_page_data.get('id')
        url = f"https://{auth_creds.get('domain')}/wiki/rest/api/content/{confluence_page_id}/label"
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps(
            [
                {
                    "prefix": "team",
                    "name": f"nuclino-id_{self.src_data.get('id')}"
                },
                {
                    "prefix": "team",
                    "name": f"nuclino-migration"
                }
            ]
        )

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )

        OUT['code'] = response.status_code
        OUT['return'] = response.json()
        OUT['status'] = True if response.status_code == 200 else False
        return OUT

    def create_page_content(self, data, logger):
        """

        :param data:
        :param logger:
        :return:
        """
        OUT = {
            'status': False,
            'msg': 'Uninitialized'
        }
        try:
            self.src_data = data
            meta_table = make_table(
                url=data['url'],
                name=data['name'],
                created_by=data['created_by']['email'],
                created_date=data['created_date'],
                updated_by=data['updated_by']['email'],
                updated_date=data['updated_date'],
                type=data['type'],
                age=data['age'],
            )
            if not meta_table or meta_table == '':
                logger.warning(f'Creating page header table failed with input data: {data}')

            # Get doc body
            preview_results = get_nuclino_page_content(data['id'])

            body = self._convert_nuclino_to_confluence_html(preview_results)

            # Format body
            self.page_content = make_page_body(
                table=meta_table,
                preview_text=preview_results[:200],
                body=body,
            )
            OUT['status'] = True
            OUT['msg'] = 'Success'
        except Exception as e:
            OUT['msg'] = str(e)

        return OUT

    def create_confluence_page(self, parent_folder):
        """

        :return:
        """
        # This code sample uses the 'requests' library:
        # http://docs.python-requests.org
        OUT = {
            'status':False,
            'msg': 'Uninitialized',
            'status_code': 600,
            'return': None
        }
        auth_creds = get_confluence_auth_creds()
        url = f"https://{auth_creds.get('domain')}/wiki/api/v2/pages"
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        retry_count = 2
        success = False
        while retry_count > 0 and not success:
            title_prefix = f'-{self.src_data.get("id")}'*(2-retry_count)
            page_title = f"{self.src_data.get('name')}{title_prefix}"
            payload = json.dumps({
                "spaceId": int(auth_creds.get('spaceID')),
                "status": "current",
                "parentId": parent_folder,
                "title": page_title,
                "body": {
                    "representation": "storage",
                    "value": self.page_content
                    # "value": '<h1>Test</h1><p>text</p>'
                }
            })

            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=headers,
                auth=auth
            )
            success = True if response.status_code == 200 else False
            retry_count -= 1

        # OUT = {
        #     'status': False,
        #     'msg': 'Uninitialized',
        #     'status-code': 600,
        #     'return': None
        # }
        OUT['status'] = True if response.status_code == 200 else False
        OUT['status_code'] = response.status_code
        OUT['return'] = response.json()
        OUT['msg'] = response.reason
        self.confluence_page_data = response.json()

        return OUT

    @staticmethod
    def create_confluence_folder(parent_folder_name):
        """

        :return:
        """
        # This code sample uses the 'requests' library:
        # http://docs.python-requests.org
        OUT = {}

        auth_creds = get_confluence_auth_creds()
        url = f"https://{auth_creds.get('domain')}/wiki/api/v2/folders"
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = json.dumps({
            "spaceId": int(auth_creds.get('spaceID')),
            "title": parent_folder_name,
        })

        response = requests.request(
            "POST",
            url,
            data=payload,
            headers=headers,
            auth=auth
        )

        OUT['code'] = response.status_code
        OUT['return'] = response.json()
        OUT['folder_id'] = response.json().get('id')
        OUT['status'] = True if response.status_code == 200 else False
        return OUT

    @staticmethod
    def set_doc_parent(nuclino_data:dict, logger):
        """
        Does current page need reparenting?
        If yes, continue
        1. Get current page by label
        2. Get parent page by label
        3. Update current page with new parent confluence id
        :return:
        """
        OUT = {
            'status': False,
            'data':None,
            'msg': 'Uninitialized'
        }
        if not nuclino_data.get('parent'):
            OUT['status'] = True
            OUT['msg'] = 'No parent adjustment needed'
            return OUT

        auth_creds = get_confluence_auth_creds()
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )
        headers_labels = {
            "Accept": "application/json",
        }

        # Get Current Page ID
        url = f"https://{auth_creds.get('domain')}/wiki/rest/api/label"

        current_page_payload = {
            "name": f"team:nuclino-id_{nuclino_data.get('id')}"
        }


        '''
        {
            "label":{
                "prefix":"<string>",
                "name":"<string>",
                "id":"<string>",
                "label":"<string>"
            },
            "associatedContents":{
                "results":[
                    {
                        "contentType":"page",
                        "contentId":2154,
                        "title":"<string>"
                    }
                ],
                "start":2154,
                "limit":2154,
                "size":2154
            }
        }
        '''
        current_page_response = requests.request(
            "GET",
            url,
            params=current_page_payload,
            headers=headers_labels,
            auth=auth
        )
        current_page_success = True if current_page_response.status_code == 200 else False
        if not current_page_success:
            logger.error(f'''Attempting to get current page info by label failed-------
NUCLINO-DATA: {pformat(nuclino_data)}
CONFLUENCE-FETCH-RESULTS: {pformat(current_page_response)}''')
            return False

        tmp_data = current_page_response.json()
        tmp_results = tmp_data.get('associatedContents', {}).get('results')
        if len(tmp_results) > 1:
            logger.error(f'More than one page found for supposedly unique ID label: {tmp_results}')
            return False
        else:
            logger.info(f'Success!! Found just one page: {tmp_results}')
        current_info = {
            'success': current_page_success,
            'page_id': tmp_results[0].get('contentId'),
            'title': tmp_results[0].get('title'),
        }

        # Get Parent Page Info
        parent_page_payload = {
            "name": f"team:nuclino-id_{nuclino_data.get('parent')}"
        }

        parent_page_response = requests.request(
            "GET",
            url,
            params=parent_page_payload,
            headers=headers_labels,
            auth=auth
        )

        parent_page_success = True if parent_page_response.status_code == 200 else False
        if not parent_page_success:
            logger.error(f'''Attempting to get current page info by label failed-------
        NUCLINO-DATA: {pformat(nuclino_data)}
        CONFLUENCE-FETCH-RESULTS: {pformat(parent_page_response)}''')
            return False

        tmp_data = parent_page_response.json()
        tmp_results = tmp_data.get('associatedContents', {}).get('results')
        if len(tmp_results) > 1:
            logger.error(f'More than one page found for supposedly unique ID label: {tmp_results}')
            return False
        else:
            logger.info(f'Success!! Found just one page: {tmp_results}')
        parent_info = {
            'success': parent_page_success,
            'page_id': tmp_results[0].get('contentId'),
            'title': tmp_results[0].get('title'),
        }

        logger.info(f'''Collected IDs are:
NUCLINO-DATA: {pformat(nuclino_data)}
CURRENT-PAGE: {pformat(current_info)}
PARENT-PAGE: {pformat(parent_info)}''')

        url = f"https://{auth_creds.get('domain')}/wiki/rest/api/content/{current_info['page_id']}/move/append/{parent_info['page_id']}"
        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "PUT",
            url,
            headers=headers,
            auth=auth
        )

        # OUT = {
        #     'status': False,
        #     'data': None,
        #     'msg': 'Uninitialized'
        # }
        OUT['status'] = True if response.status_code == 200 else False
        OUT['data'] = response.json()
        OUT['msg'] = f'{response.reason} - {response.text}'

        logger.info(f'RESULTS: {pformat(OUT)}')

        return OUT['status']