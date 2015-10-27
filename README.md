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

download_file(FILE ID HERE)
```

Download all files in folder
```python
from googleDriveConnector import download_files_in_folder

download_files_in_folder(FOLDER ID HERE)
```
