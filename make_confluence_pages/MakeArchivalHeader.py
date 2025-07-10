"""
Create the Archival Information Table
"""

template_table = '''<table data-table-width="760" data-layout="default">
    <tbody>
        <tr>
            <td><p><strong>Source URL</strong></p></td>
            <td><p>---URL---</p></td>
            <td><p><strong>Name</strong></p></td>
            <td><p>---DOC_NAME---</p></td>
        </tr>
        <tr>
            <td><p><strong>Created By</strong></p></td>
            <td><p>---CREATED_BY---</p></td>
            <td><p><strong>Created Date</strong></p></td>
            <td><p>---CREATED_DATE---</p></td>
        </tr>
        <tr>
            <td><p><strong>Updated By</strong></p></td>
            <td><p>---UPDATED_BY---</p></td>
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
    if None in [url, name, created_by, created_date, type, updated_by, updated_date, age]:
        return ''

    msg = template_table.replace('---URL---', url)
    msg = msg.replace('---DOC_NAME---', name)
    msg = msg.replace('---CREATED_BY---', created_by)
    msg = msg.replace('---CREATED_DATE---', created_date)
    msg = msg.replace('---UPDATED_BY---', updated_by)
    msg = msg.replace('---UPDATED_DATE---', updated_date)
    msg = msg.replace('---DOC_TYPE---', type)
    msg = msg.replace('---DOC_AGE---', age)

    return msg

