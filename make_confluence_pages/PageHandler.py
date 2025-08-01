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
import logging

import markdown
import mimetypes
import os
from pprint import pprint, pformat
import re
import sys
import requests
from requests.auth import HTTPBasicAuth
import json

from make_confluence_pages.MakeTemplateDoc import make_page_body, make_workspace_body
from make_confluence_pages.MakeArchivalHeader import make_table
from make_confluence_pages.GetNuclinoContent import get_nuclino_page_content
from auth_creds.confluence_creds import get_confluence_auth_creds
from auth_creds.nuclino_creds import get_nuclino_auth_request, get_nuclino_auth_creds

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

    def _make_documentation_page(self, data, logger):
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

    def _make_workspace_page(self, data, logger):
        OUT = {
            'status': False,
            'msg': 'Uninitialized'
        }
        try:
            self.src_data = data


            # Format body
            self.page_content = make_workspace_body()
            OUT['status'] = True
            OUT['msg'] = 'Success'
        except Exception as e:
            OUT['msg'] = str(e)

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
            if data['type'] == 'Document':
                ## Creating content for a workspace
                OUT = self._make_documentation_page(data, logger)
            else:
                ## Creating content for a page
                OUT = self._make_workspace_page(data, logger)
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
        if len(tmp_results) != 1:
            logger.error(f'More, or less, than one page found for supposedly unique ID label: {tmp_results}')
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

    @staticmethod
    def get_confluence_page_id(nuclino_data:dict, logger):
        """

        :param nuclino_data:
        :param logger:
        :return:
        """
        OUT = {
            'status': False,
            'msg': 'Unitialized',
            'confluence_id': None
        }
        auth_creds = get_confluence_auth_creds()
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )
        headers = {
            "Accept": "application/json"
        }

        # Get Current Page ID
        url = f"https://{auth_creds.get('domain')}/wiki/rest/api/label"
        current_page_payload = {
            "name": f"team:nuclino-id_{nuclino_data.get('id')}"
        }
        current_page_response = requests.request(
            "GET",
            url,
            params=current_page_payload,
            headers=headers,
            auth=auth
        )
        current_page_success = True if current_page_response.status_code == 200 else False
        if not current_page_success:
            msg = f'''Attempting to get current page info by label failed-------
        NUCLINO-DATA: {pformat(nuclino_data)}
        CONFLUENCE-FETCH-RESULTS: {pformat(current_page_response)}'''
            logger.error(msg)
            OUT['msg'] = msg
            return OUT
        tmp_data = current_page_response.json()

        # Upload content to page
        OUT['status'] = True
        OUT['msg'] = 'Success'
        OUT['confluence_page_id'] = tmp_data.get('associatedContents').get('results')[0].get('contentId')
        return OUT

    @staticmethod
    def download_image_from_nuclino_page(nuclino_data:dict, logger:logging.Logger, settings:dict):
        """
        {
          "status": "success",
          "data": {
            "object": "file",
            "id": "eec0a152-b1e9-43fd-bef8-987f95c85c6e",
            "itemId": "dd9a69db-048d-4644-8738-36bee31bbee0",
            "fileName": "screenshot.png",
            "createdAt": "2021-12-15T07:58:11.196Z",
            "createdUserId": "2e96f3bb-c742-4164-af2c-151ab2fd346b",
            "download": {
              "url": "https://nuclino-files.s3.eu-central-1.amazonaws.com/a122ab11...",
              "expiresAt": "2021-12-15T08:08:49.931Z"
            }
          }
        }

        :param nuclino_data:
        :param logger:
        :param settings:
        :return:
        """
        OUT = {
            'status': False,
            'msg': '',
            'files': []
        }
        # auth_creds = get_nuclino_auth_creds()
        headers = get_nuclino_auth_request()

        for doc_file_id in nuclino_data.get('fileIDs', []):
            url = f"https://api.nuclino.com/v0/files/{doc_file_id}"
            response = requests.get(
                url,
                headers=headers
            )

            logger.info(response.json())
            if response.status_code != 200 or response.json().get('status') != 'success':
                OUT['msg'] = f'{response.reason} - {response.text}'
                return OUT

            data = response.json().get('data')
            filename = f'{nuclino_data.get("id")}_{doc_file_id}_{data.get("fileName")}'
            download_fullpath = os.path.normpath(
                os.path.join(
                    str(settings.get('files').get('attachmentdownloadlocation')),
                    filename
                )
            )

            download_url = data.get('download').get('url')  # Replace with your file URL
            download_response = requests.get(download_url)

            if download_response.status_code != 200:
                OUT['msg'] = f'''Download failed for: {download_fullpath}
With message: {download_response.reason} & {download_response.text}'''
                return OUT

            # Save the file locally
            with open(download_fullpath, 'wb') as f:
                f.write(download_response.content)

            OUT['msg'] += f'Downloaded {data.get("fileName")} to {download_fullpath}\n'
            OUT['files'].append(download_fullpath)

            
        OUT['status'] = True
        OUT['msg'] = f'''SUCCESS:
{OUT["msg"]}'''

        return OUT

    @staticmethod
    def attach_file_to_confluence_page_object(nuclino_data, file_download, confluence_page_id, logger):
        """

        :param nuclino_data:
        :param file_download:
        :param confluence_page_id:
        :param logger:
        :return:
        """
        OUT = {
            'status': False,
            'msg': 'Unitialized'
        }
        auth_creds = get_confluence_auth_creds()
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )
        headers = {
            "Accept": "application/json"
        }
        url = f"https://{auth_creds.get('domain')}/wiki/rest/api/content/{confluence_page_id}/child/attachment"
        filename = os.path.basename(file_download)
        comment, anon = mimetypes.guess_type(filename)
        headers = {
            'X-Atlassian-Token': 'nocheck',
        }
        files = {
            'file': open(file_download, 'rb'),
            'minorEdit': (None, 'true'),
            'comment': (None, 'Attachment Migration from Nuclino', comment),
        }

        upload_response = requests.post(
            url=url,
            headers=headers,
            files=files,
            auth=auth,
        )

        if upload_response.status_code != 200:
            msg = f'''Failed to upload the attachment: {file_download} to document id: {confluence_page_id}
ERROR Message: {upload_response.reason}. {upload_response.text}'''
            OUT['msg'] = msg
            return OUT

        OUT['status'] = True
        OUT['msg'] = f'''Successful upload of attachment ({file_download})
{upload_response.reason}. {upload_response.text}'''
        return OUT

    @staticmethod
    def get_confluence_page_attachment_replacements(nuclino_data, file_download, confluence_page_id, logger):
        '''

        :param nuclino_data:
        :param file_download:
        :param confluence_page_id:
        :param logger:
        :return:
        '''
        # Get Confluence Page Data
        '''
        {
          "id": "<string>",
          "status": "current",
          "title": "<string>",
          "spaceId": "<string>",
          "parentId": "<string>",
          "parentType": "page",
          "position": 57,
          "authorId": "<string>",
          "ownerId": "<string>",
          "lastOwnerId": "<string>",
          "createdAt": "<string>",
          "version": {
            "createdAt": "<string>",
            "message": "<string>",
            "number": 19,
            "minorEdit": true,
            "authorId": "<string>"
          },
          "body": {
            "storage": {},
            "atlas_doc_format": {},
            "view": {}
          },
        }
        '''
        OUT = {
            'status': False,
            'msg': 'Unitialized',
            'replacement': {
                'before': '',
                'after': '',
                'version': 0,
                'body': '',
                'title': ''
            }
        }
        auth_creds = get_confluence_auth_creds()
        auth = HTTPBasicAuth(
            auth_creds.get('user'),
            auth_creds.get('key'),
        )
        headers = {
            "Accept": "application/json"
        }
        params = {
            'body-format': 'storage'
        }

        url = f"https://{auth_creds.get('domain')}/wiki/api/v2/pages/{confluence_page_id}"
        confluence_page_response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=auth,
            params=params
        )

        if confluence_page_response.status_code != 200:
            OUT['msg'] = f'''Failed to collect confluence page data from id: {confluence_page_id}
ERROR Message: {confluence_page_response.reason}. {confluence_page_response.text}'''
            return OUT

        content_body = confluence_page_response.json().get('body').get('storage')
        content_version = int(confluence_page_response.json().get('version').get('number'))
        title = confluence_page_response.json().get('title')

        if not content_body:
            OUT['status'] = True
            OUT['msg'] = 'No content body'

        if not content_version:
            OUT['status'] = False
            OUT['msg'] = 'Collecting page version failed'
            return OUT

        file_id = file_download.split('_',2)[-1]
        file_basename = file_download.split('_')[-1]
        # old_nuclino_file_link_re = f"<a href=\\\"https://files.nuclino.com/files/[a-z-_0-9]*({file_id}).*</a>"
        # old_nuclino_img_link_re = f"<img alt=\"({file_basename})\" src=\".*({file_basename})\".?/>"
        re_nuclino_searches = [
            f"<a href=\\\"https://files.nuclino.com/files/[a-z-_0-9]*/({file_id}).*</a>",
            f"<img alt=\"({file_basename})\" src=\".*({file_basename})\".?/>"
        ]

        re_results = None
        for re_search in re_nuclino_searches:
            re_results = re.search(re_search, content_body.get('value'))
            if re_results:
                break
        # matches = re_results.groups()

        swap = ''
        file_type = 'image' if file_download.split('.')[1] in ['png', 'jpg', 'jpeg', 'gif', 'tga', 'bmp'] else 'file'
        filename = os.path.basename(file_download)

        if file_type == 'image':
            swap = f'''
<ac:{file_type}>
  <ri:attachment ri:filename="{filename}" />
</ac:{file_type}>
'''
        else:
            swap = f'''
<p class="media-group">
    <ac:structured-macro ac:name="view-file" ac:schema-version="1">
        <ac:parameter ac:name="name">
            <ri:attachment ri:filename="{filename}" />
        </ac:parameter>
    </ac:structured-macro>
<p />
'''
        # content_body.get('value').replace(re_results.group(0), swap)
        found_section = re_results.group(0)
        new_content = content_body.get('value')
        new_content = new_content.replace(found_section, swap)
        content_version += 1

        OUT['replacement']['before'] = found_section
        OUT['replacement']['after'] = swap
        OUT['replacement']['version'] = content_version
        OUT['replacement']['body'] = new_content
        OUT['replacement']['title'] = title

        OUT['status'] = True
        OUT['message'] = 'Success'

        # return OUT

        '''
        </tr>\n    
</tbody>\n
</table>\n
</ac:layout-cell>
</ac:layout-section>\n
<ac:layout-section ac:type=\"two_equal\" ac:breakout-mode=\"default\">
   <ac:layout-cell>
       <h1>Table of Contents</h1>
       <ac:structured-macro ac:name=\"toc\" ac:schema-version=\"1\" data-layout=\"default\" ac:macro-id=\"756d9a45-0e62-4c5b-9472-5ced60708d79\">
           <ac:parameter ac:name=\"minLevel\">1</ac:parameter>
           <ac:parameter ac:name=\"maxLevel\">2</ac:parameter>
           <ac:parameter ac:name=\"outline\">false</ac:parameter>
           <ac:parameter ac:name=\"style\">none</ac:parameter>
           <ac:parameter ac:name=\"type\">list</ac:parameter>
           <ac:parameter ac:name=\"printable\">true</ac:parameter>
       </ac:structured-macro>
   </ac:layout-cell>\n\n
   <ac:layout-cell>\n
       <h1>Child Pages</h1>\n
       <ac:structured-macro ac:name=\"children\" ac:schema-version=\"2\" data-layout=\"default\" ac:macro-id=\"55f9e977-282a-4f87-b76d-4d590d85960a\">
           <ac:parameter ac:name=\"all\">true</ac:parameter>
           <ac:parameter ac:name=\"depth\">3</ac:parameter>
       </ac:structured-macro>\n
   </ac:layout-cell>
</ac:layout-section>
<ac:layout-section ac:type=\"fixed-width\" ac:breakout-mode=\"default\">
   <ac:layout-cell>\n
       <hr />\n
       <h1>Original Document</h1>\n
       <p>
           <br />
       </p>\n
       <p>
           <a href=\"https://files.nuclino.com/files/4284b5d9-771e-4e32-8dd1-9aa0d3ac3375/Riviana_New_Bundle_Workbook_Example.xlsx\">Riviana_New_Bundle_Workbook_Example.xlsx</a>
       </p>\n
   </ac:layout-cell>
</ac:layout-section>
</ac:layout>"
        '''



        return OUT
