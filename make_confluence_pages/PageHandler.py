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
load_import_from = os.path.join(os.path.abspath(os.getcwd()), 'import.py')



# Load the main module
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

    def create_confluence_page(self):
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

        return True if response.status_code == 200 else False