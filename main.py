from __future__ import print_function

import io
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveHelper:

    def __init__(self):
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('drive', 'v3', credentials=self.creds)

    def download_media_as_xlsx(self, file_id):
        request = self.service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.FileIO('sheet.xlsx', mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def download_media(self, file_id, filename, out_dir='images'):
        request = self.service.files().get_media(fileId=file_id)
        os.makedirs(out_dir, exist_ok=True)
        path = out_dir + '/' + filename
        if not os.path.isfile(path):
            fh = io.FileIO(path, mode='wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
        else:
            print(f'File exists: {filename}')

    def download_files_from_dir(self, dir_id):
        page_token = None
        while True:
            response = self.service.files().list(q=f"'{dir_id}' in parents",
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id, name)',
                                                 pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                self.download_media(file.get('id'), file.get('name'))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break


def main():
    helper = GoogleDriveHelper()
    helper.download_media_as_xlsx('1RlD9sT_K5CRWsCLeLSBogOiqwSyfi6YnC2pCk1WKfsc')
    helper.download_files_from_dir('14c5B5kLAbpBsWcNr6tsVRMgTshiyxmfZ')


if __name__ == '__main__':
    main()
