#!/usr/bin/env python

from __future__ import print_function
import os
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import io

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class GollogDrive(object):
    def __init__(self, client_secret_file):
        self.scopes = 'https://www.googleapis.com/auth/drive'
        self.client_secret_file = client_secret_file

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive_creds.json')
        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)

        self.credentials = credentials
        self.drive_service = build('drive', 'v3', http=self.credentials.authorize(Http()))

    def list_files(self):
        """
        List some of the files on the Drive.
        :returns: A dictionary containing the list of file-details.
        """
        file_service = self.drive_service.files()
        results = file_service.list(pageSize=10, fields="files(id, name)").execute()
        print (results)
        return results

    def file_exists(self, fileId):
        """
        Checks whether a file exists on the Drive and is not trashed.
        :param fileId: The ID of the file to check.
        :type fileId: str
        :returns: bool
        """
        if not fileId:
            return False
        try:
            file_service = self.drive_service.files()
            results = file_service.get(fileId=fileId, fields="trashed").execute()
            # Return False if the file is either trashed or does not exist
            return not results['trashed']
        except Exception:
            return False

    def create_file(self, file_path, parentId=None):
        """
        Creates a new file on the Drive.
        :param file_path: The path of the source file on local storage.
        :type file_path: str
        :param parentId: The ID of the directory in which the file has to be
         created. If it is None, the file will be created in the root directory.
        :type parentId: str or None
        :returns: A dictionary containing the ID of the file created.
        """
        file_service = self.drive_service.files()
        media_body = MediaFileUpload(file_path)

        body = {'name': os.path.basename(file_path)}
        if parentId:
            body['parents'] = [parentId]

        results = file_service.create(
            body=body, media_body=media_body, fields="id").execute()

        return results

    def update_file(self, file_path, fileId):
        """
        Modifies an already existing file on the Drive.
        :param file_path: The path of the source file on local storage.
        :type file_path: str
        :param fileId: The ID of the file to be modified.
        :type fileId: str
        :returns: A dictionary containing the ID of the file modified.
        """
        file_service = self.drive_service.files()
        media_body = MediaFileUpload(file_path)

        results = file_service.update(
            fileId=fileId, media_body=media_body, fields="id").execute()

        return results

    def update_or_create_file(self, file_dict):
        """
        Updates the file if it exists already on the Drive, else creates a new one.
        :param file_dict: A dictionary containing the details about the file.
         The required keys are 'path', 'fileId' and 'parentId'.
        :type file_dict: dict
        :returns: A dictionary containing the details about the file.
        """
        file_path = file_dict['path']
        fileId = file_dict['fileId']
        parentId = file_dict.get('parentId', None)

        if self.file_exists(fileId):
            return self.update_file(file_path, fileId)
        else:
            return self.create_file(file_path, parentId)

    def download_all_files(self):
        """

        :param files_to_download: Name of a single file or list containing multiple files.
        :return:
        """
        file_service = self.drive_service.files()
        # files_to_download = file_service.list().execute()
        files_to_download = file_service.list(pageSize=10, fields="files(id, name, mimeType)").execute()
        print (files_to_download)
        for file_to_download in files_to_download['files']:
            if file_to_download['mimeType'] == 'application/x-gzip':
                print (file_to_download['id'], file_to_download['name'])
                #data = file_service.export(fileId=file_to_download['id'], mimeType=file_to_download['mimeType']).execute()
                request = file_service.get_media(fileId=file_to_download['id'])
                fn = '%s' % file_to_download['name']
                with open(fn, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print ("Download %d%%." % int(status.progress() * 100))
                print ("Downloaded %s" % file_to_download['name'])

CLIENT_SECRET_FILE = 'client_secret.json'
gd = GollogDrive(CLIENT_SECRET_FILE)
gd.download_all_files()
#file_dict = dict()
#file_dict['path'] = "yes.txt"
#file_dict['fileId'] = 24434
#gd.update_or_create_file(file_dict)
#gd.list_files()
#gd.download('hello.txt')
