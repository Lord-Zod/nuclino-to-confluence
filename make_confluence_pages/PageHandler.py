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


from MakeTemplateDoc import make_page_body
from MakeArchivalHeader import make_table

class PageHandler(object):
    """

    """
    def __init__(self, **data):
        self.age = data['age']
        self.id = data['id']
        self.type = data['type']
        self.name = data['name']
        

    # def