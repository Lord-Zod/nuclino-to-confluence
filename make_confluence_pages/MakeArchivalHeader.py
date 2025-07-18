"""
Create the Archival Information Table
"""

template_table = '''<table data-table-width="760" data-layout="default">
    <tbody>
        <tr>
            <td><p><strong>Source URL</strong></p></td>
            <td><p><a href="---URL---" target="_blank">Link to Nuclino Page</a></p></td>
            <td><p><strong>Name</strong></p></td>
            <td><p>---DOC_NAME---</p></td>
        </tr>
        <tr>
            <td><p><strong>Created By</strong></p></td>
            <td><p><a href="mailto:---CREATED_BY---">---CREATED_BY---</a></p></td>
            <td><p><strong>Created Date</strong></p></td>
            <td><p>---CREATED_DATE---</p></td>
        </tr>
        <tr>
            <td><p><strong>Updated By</strong></p></td>
            <td><p><a href="mailto:---UPDATED_BY---">---UPDATED_BY---</a></p></td>
            <td><p><strong>Updated Date</strong></p></td>
            <td><p>---UPDATED_DATE---</p></td>
        </tr>
        <tr>
            <td><p><strong>Type</strong></p></td>
            <td><p>---DOC_TYPE---</p></td>
            <td><p><strong>Age</strong></p></td>
            <td><p>---DOC_AGE---</p></td>
        </tr>
    </tbody>
</table>'''

def make_table(
        url:str,
        name:str,
        created_by:str,
        created_date:str,
        updated_by:str,
        updated_date:str,
        type:str,
        age:str,
)->str:
    """

    :param url:
    :param name:
    :param created_by:
    :param created_date:
    :param updated_by:
    :param updated_date:
    :param type:
    :param age:
    :return:
    """
    # if None in [url, name, created_by, created_date, type, updated_by, updated_date, age]:
    #     return ''

    local_args = [
        x if x else '' for x in [url, name, created_by, created_date, updated_by, updated_date, type, age]
    ]

    msg = template_table.replace('---URL---', local_args[0])
    msg = msg.replace('---DOC_NAME---', local_args[1])
    msg = msg.replace('---CREATED_BY---', local_args[2])
    msg = msg.replace('---CREATED_DATE---', local_args[3])
    msg = msg.replace('---UPDATED_BY---', local_args[4])
    msg = msg.replace('---UPDATED_DATE---', local_args[5])
    msg = msg.replace('---DOC_TYPE---', local_args[6])
    msg = msg.replace('---DOC_AGE---', local_args[7])

    return msg

