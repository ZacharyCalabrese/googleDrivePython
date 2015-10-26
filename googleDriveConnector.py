import httplib2
import os
import oauth2client

from apiclient import errors, http, discovery
from oauth2client import client, tools
import config

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    """
    Checks to see if user credentials are already in storage at ~/.credentials.

    If nothing has been stored, or if the stored credentials are invalid, the 
    OAuth2 flow is completed to obtain the new credentials.

    Notice: If you are having trouble accessing dirve it may be that the credentials
    stored are for a user account that does have access to the specified file / folder

    Returns: the obtained credentials
    """

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(config.CLIENT_SECRET_FILE, config.SCOPES)
        flow.user_agent = config.APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials

def setup_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    return service

def get_filename(service, file_id):
    """
    Return the title of the referenced file as it appears on Google Drive
    """

    try:
        file = service.files().get(fileId=file_id).execute()
        title = file['title']

        return title 
    except Exception as error:
        print 'An error occurred: %s' % error
        return None

def download_file(file_id, destination_folder = ""):
    """
    Download a Drive file's content to the local filesystem.
        
    Args:
    file_id: ID of the Drive file that will downloaded.
    """

    service = setup_service()
    filename = get_filename(service, file_id)
    if len(destination_folder) > 0:
        local_fd = open(destination_folder + "/" + filename, "w+")
    else:
        local_fd = open(filename, "w+")    
    request = service.files().get_media(fileId=file_id)
    media_request = http.MediaIoBaseDownload(local_fd, request)
                    
    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            return
        if download_progress:
            print 'Download Progress: %d%%' % int(download_progress.progress() * 100)
        if done:
            print 'Download Complete'
            return
    return service

def download_files_in_folder(folder_id, destination_folder = ""):
    service = setup_service()
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.children().list(folderId=folder_id, **param).execute()
            for child in children.get('items', []):
                download_file(child['id'], destination_folder)
            page_token = children.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break
