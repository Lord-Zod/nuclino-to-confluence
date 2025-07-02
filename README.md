![Project Status](https://img.shields.io/badge/status-in_progress-orange)

# Overview
A series of python scripts to import Nuclino Workspaces, with archival and history information, into a Confluence Space

This is a [fork of a repo from bitrise-io](https://github.com/bitrise-io/nuclino-to-confluence) which itself is based on the [Markdown to Confluence Page](https://github.com/rittmanmead/md_to_conf) script by [Rittman Mead](https://github.com/RittmanMead)



## Requirements

Python3 and pip3 are required to run this script, if you do not have them already follow these steps

## Usage - `get_nuclino_entity_tree.py`

The purpose of this is to analyze the entity relationships between docs and the general site complexity
It will create a map of docs as a yaml file

### Function - `get_workspaces`
Uses the credentials supplied in `.password_file_ini` to get the list of workspaces for your site.
Returns a dictionary in this form:
```
{ 
    workspace_name: 
    {
        'id': <alphanumeric unique ID of the workspace>,
        'name': <string, name of the workspace>
        'childIds': <list of the unique IDs of the first level children items in the workspace>
# nuclino-to-confluence
    }
}
```

## Usage - `import.py`

- In Nuclino administrators can [export workspaces](https://help.nuclino.com/fb60e6f6-export-a-workspace) in the Markdown format, this operation will create a folder with a bunch of .md files.
- Clone this repo
- Install the migration script’s dependencies with
```SHELL
pip3 install -r requirements.txt
```
- Create an [API token](https://id.atlassian.com/manage/api-tokens) for Confluence
- Export the following environment variables:
```SHELL
export CONFLUENCE_ORGNAME=bitrise
export CONFLUENCE_USERNAME=your.username@bitrise.io
export CONFLUENCE_PASSWORD=yourAPItoken
```
- Run the script with
```SHELL
python3 import.py SPACEKEY path/to/export/folder plan
```
Where **SPACEKEY** is your Confluence Space’s key (e.g.: INFRA for the Infra team - https://bitrise.atlassian.net/wiki/spaces/INFRA) and **path/to/export/folder** is the folder where you keep the exported .md files from Nuclino
This will create a subfolder named **plan** with similar structure you had in Nuclino, you may remove or edit these files in the **plan** folder:
- The **index.md** will be the entry-point of the execution
- Every file that is in the same format as the **index.md** file will be considered as an index-file
- Every index-file, beside **index.md** represents a subfolder
- In the **plan** folder IDs has been removed from folder names, but they are still present as suffix on .md files, do not remove them manually, or the execution will mess up your page-names
- Avoid name-duplication! (pages with the same names in **other** Spaces won't be a problem)
- When you satisfied with the plan you can run
```SHELL
python3 import.py SPACKEY path/to/export/folder execute
```
This will create the pages in Confluence under your Space (it won’t mess up already existing pages with the same name, but it is not advised to execute the plan many times)

pls keep in mind that Nuclino exports its content to Markdown, and the script turns that into HTML and sends it that way to Confluence, so the translation may not be 100% purrfect 😽
