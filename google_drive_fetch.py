import os
import json
import io
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    key_data = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY', '')
    if os.path.isfile(key_data):
        creds = service_account.Credentials.from_service_account_file(key_data, scopes=SCOPES)
    else:
        key_dict = json.loads(key_data)
        creds = service_account.Credentials.from_service_account_info(key_dict, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def fetch_videos():
    folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '')
    if not folder_id:
        print("[SKIP] No GOOGLE_DRIVE_FOLDER_ID set")
        return []

    os.makedirs('Videos', exist_ok=True)

    service = get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'video/' and trashed=false",
        fields="files(id, name, mimeType)",
        orderBy="createdTime desc"
    ).execute()

    files = results.get('files', [])
    if not files:
        print("[INFO] No new videos found in Google Drive folder")
        return []

    downloaded = []
    for f in files:
        filepath = os.path.join('Videos', f['name'])
        if os.path.exists(filepath):
            print(f"[SKIP] Already downloaded: {f['name']}")
            continue

        print(f"[DOWNLOAD] {f['name']}...")
        request = service.files().get_media(fileId=f['id'])
        fh = io.FileIO(filepath, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"  Download {int(status.progress() * 100)}%")

        print(f"  Saved: {filepath}")
        downloaded.append(filepath)

    return downloaded

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    videos = fetch_videos()
    print(f"\nTotal new videos downloaded: {len(videos)}")
