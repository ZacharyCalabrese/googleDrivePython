# GoogleDrivePython

### Usage
To connect with Google Drive using Python you will need to activate the Google Drive API. Instructions for that can be found here: https://developers.google.com/drive/web/quickstart/python

You will also need to install the Google Client Library
```
pip install --upgrade google-api-python-client
```

To use this module you will need to setup a config file (config.py) specifying the following and place it in the same directory as googleDriveConnector.py:
```python
# https://developers.google.com/drive/web/scopes
SCOPES = 'DESIRED API SCOPES' 
CLIENT_SECRET_FILE = 'YOUR JSON CLIENT SECRET FILE PATH AND FILE NAME'
APPLICATION_NAME = 'YOUR APP NAME'
```

Download specific file
```python
from googleDriveConnector import download_file 

download_file('FILE ID HERE')
```

Download all files in folder
```python
from googleDriveConnector import download_files_in_folder

download_files_in_folder('FOLDER ID HERE')
```

Delete specific file
```python
from googleDriveConnector import delete_file

delete_file('FILE ID')
```

Move file from one folder to another
```python
from googleDriveConnector import move_file_to_folder

move_file_to_folder('FILE ID HERE', 'DESTINATION FOLDER ID')
```

Upload file
```python
from googleDriveConenctor import push_file_to_drive

push_file_to_drive('ABSOLUTE PATH AND FILE NAME', 'DESIRED TITLE AND EXTENSION', 'DESCRIPTION', 'DESTINATION FOLDER ID')
