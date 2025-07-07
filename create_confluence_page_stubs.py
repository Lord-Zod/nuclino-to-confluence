# Read Doc YAML
# For Each Doc
# ... Create Doc in Space
# ... Add Table with Archival Info
# ... Add title
# PYTHON IMPORTS
import yaml


def create_single_page(data_in)->bool:
    """

    :param data_in:
    :return:
    """
    # This code sample uses the 'requests' library:
    # http://docs.python-requests.org
    import requests
    from requests.auth import HTTPBasicAuth
    import json

    url = "https://{your-domain}/wiki/api/v2/pages"

    auth = HTTPBasicAuth("email@example.com", "<api_token>")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "spaceId": "<string>",
        "status": "current",
        "title": "<string>",
        "parentId": "<string>",
        "body": {
            "representation": "storage",
            "value": "<string>"
        },
        "subtype": "live"
    })

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

def make_docs():
    """

    :return:
    """
    data = {}
    with open('nuclino_entity_tree.yaml', 'r') as docs_file:
        data = yaml.safe_load(docs_file)

    for doc in data:
