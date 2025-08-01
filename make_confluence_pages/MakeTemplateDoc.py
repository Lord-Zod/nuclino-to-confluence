"""
Template for Confluence Body
"""


page_body = '''<ac:layout><ac:layout-section ac:type="fixed-width" ac:breakout-mode="default"><ac:layout-cell>
---ARCHIVAL_TABLE---
</ac:layout-cell></ac:layout-section>
<ac:layout-section ac:type="two_equal" ac:breakout-mode="default"><ac:layout-cell><h1>Table of Contents</h1><ac:structured-macro ac:name="toc" ac:schema-version="1" data-layout="default"><ac:parameter ac:name="minLevel">1</ac:parameter><ac:parameter ac:name="maxLevel">2</ac:parameter>
<ac:parameter ac:name="outline">false</ac:parameter><ac:parameter ac:name="style">none</ac:parameter><ac:parameter ac:name="type">list</ac:parameter><ac:parameter ac:name="printable">true</ac:parameter></ac:structured-macro></ac:layout-cell>

<ac:layout-cell>
<h1>Child Pages</h1>
<ac:structured-macro ac:name="children" ac:schema-version="2" data-layout="default">
<ac:parameter ac:name="all">true</ac:parameter><ac:parameter ac:name="depth">3</ac:parameter>
</ac:structured-macro>
</ac:layout-cell></ac:layout-section><ac:layout-section ac:type="fixed-width" ac:breakout-mode="default"><ac:layout-cell>
<hr />
<h1>Original Document</h1>
---BODY_TEXT---
</ac:layout-cell></ac:layout-section></ac:layout>
'''

workspace_body = '''<ac:structured-macro ac:name="children" ac:schema-version="2" data-layout="default">
<ac:parameter ac:name="depth">3</ac:parameter>
<ac:parameter ac:name="allChildren">true</ac:parameter>
<ac:parameter ac:name="style" />
<ac:parameter ac:name="sort">title</ac:parameter>
<ac:parameter ac:name="sortAndReverse">title</ac:parameter>
<ac:parameter ac:name="first">0</ac:parameter>
</ac:structured-macro>
<p />
'''

def make_page_body(
        table:str,
        preview_text:str,
        body:str,
)->str:
    """
    creates a Confluence "storage" object
    :param table:
    :param preview_text:
    :param body:
    :return:
    """
    if None in [table, preview_text, body]:
        return ''

    msg = page_body.replace('---ARCHIVAL_TABLE---', table)
    msg = msg.replace('---PREVIEW_TEXT---', preview_text)
    msg = msg.replace('---BODY_TEXT---', body)

    return msg

def make_workspace_body():
    """

    :return:
    """
    return workspace_body