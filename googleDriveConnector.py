import httplib2
import os
import oauth2client

from apiclient import errors, http, discovery
from apiclient.http import MediaFileUpload
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

    Returns:
        The returned credentials
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
    """
    Sets up a service by authorizing credentials and establishing a http connection

    Returns:
        Connected service instance
    """

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    return service

def delete_file(file_id):
    """
    Deletes a file from Google Drive

    Args:
        file_id (string): Id of file to be deleted

    Returns:
        bool: True if successfully deleted, False if not
    """

    service = setup_service()

    try:
        service.files().delete(fileId=file_id).execute()
        print 'File %s deleted successfully' % file_id
        return True
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        return False
    
def get_filename(service, file_id):
    """
    Return the title of the referenced file as it appears on Google Drive

    Args:
        service: Service instance
        file_id (string): Id of file to be downloaded

    Returns:
        title (string): String version of file title
        None: If an error occurs on fetching file title
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
        file_id (string): ID of the Drive file that will downloaded
        destination_folder (string): Folder path on source machine where
            file is to be downloaded

    Returns:
        bool: True if successfully downloaded, False if not
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
            return False
        if download_progress:
            print 'Download Progress: %d%%' % int(download_progress.progress() * 100)
        if done:
            print 'Download Complete'
            return True

def download_files_in_folder(folder_id, destination_folder = ""):
    """
    Download all files in a folder to the local filesystem

    Args:
        folder_id (string): ID of the Drive folder to access
        destination_folder (string): Folder path on source machine where
            files are to be downloaded

    Returns:
        bool: True if successfully downloaded all files, False if not
    """

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
            return False

    return True

def get_parent_id(service, file_id):
    """
    Get the ID of the parent folder for the specified file

    Args:
        service: Service instance
        file_id (string): ID of the file for parent lookup
    
    Returns:
        parent_id (string): ID of parent folder
        None: If an error occurs

    """

    try:
        parents = service.parents().list(fileId=file_id).execute()

        return parents['items'][0]['id']
    except errors.HttpError, error:
        print 'An error occur %s' % error
        return None

def move_file_to_folder(file_id, new_folder_id = "root"):
    """
    Transfer file to a new folder

    Args:
        file_id (string): ID of the file to be moved
        folder_id (string): ID of the folder where file is to be moved;
            leave blank to move to base folder

    Returns:
        bool: True if successfully moves, False if not
    """
   
    service = setup_service()
    new_parent = {'id': new_folder_id}
    old_parent = get_parent_id(service, file_id)

    try:
        service.parents().insert(fileId=file_id, body=new_parent).execute()
        service.parents().delete(fileId=file_id, parentId=old_parent).execute()
        print 'File %s successfully moved' % file_id
        return True
    except errors.HttpError, error: 
        print 'An error occur: %s' % error
        return False

def push_file_to_drive(file_path, file_title, description = "", destination_folder = "root"):
    """
    Upload a file from local machine to Google Drive.  Include folder ID or leave
    as is to upload to root directory on Google Drive

    MAX File Size: 5120GB

    Args:
        file_path (string): Absolute path of file on machine to upload
        file_title (string): Title of uploaded file, including extension
        description (string): Description of uploaded file
        destination_folder (string): ID of folder on Google Drive

    Returns:
        bool: True if successfully uploaded, False if not
    """

    service = setup_service()
    media_body = MediaFileUpload(file_path, mimetype='[*/*]', resumable=True)
    body = {
            'title':file_title,
            'description':description,
            'parents':destination_folder,
            'mimeType':'[*/*]'
            }

    try:
        file = service.files().insert(body=body,media_body=media_body).execute()
        print 'File uploaded successfuly'
        return True
    except errors.HttpError, error:
        print 'An error occured: %s' % error
        return False















