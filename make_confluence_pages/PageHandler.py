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
from pprint import pprint
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

        payload = json.dumps( [
            {
                "prefix": "global",
                "name": f"nuclino-id_{self.src_data.get('id')}"
            }]
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

    def create_page_content(self, data):
        """

        :param data:
        :return:
        """
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

        # Get doc body
        preview_results = get_nuclino_page_content(data['id'])

        body = self._convert_nuclino_to_confluence_html(preview_results)

        # Format body
        self.page_content = make_page_body(
            table=meta_table,
            preview_text=preview_results[:200],
            body=body,
        )

        print(self.page_content)

    def create_confluence_page(self, parent_folder):
        """

        :return:
        """
        # This code sample uses the 'requests' library:
        # http://docs.python-requests.org

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

        payload = json.dumps({
            "spaceId": int(auth_creds.get('spaceID')),
            "status": "current",
            "parentId": parent_folder,
            "title": self.src_data.get('name'),
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

        tmp = response.json()
        pprint(tmp)
        self.confluence_page_data = tmp

        return True if response.status_code == 200 else False

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
    def set_doc_parent(nuclino_data:dict):
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

        payload = json.dumps({
            "name": f"nuclino-id_{nuclino_data.get('id')}"
        })

        response = requests.request(
            "GET",
            url,
            params=payload,
            headers=headers_labels,
            auth=auth
        )
