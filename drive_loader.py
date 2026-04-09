import io
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_NAME = "Fiskars_Input"
FILE_NAME = "input.xlsx"


def download_file():
    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw_json:
        raise ValueError("Переменная GOOGLE_SERVICE_ACCOUNT_JSON не задана")

    service_account_info = json.loads(raw_json)

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    # Найти папку
    folder_result = service.files().list(
        q=f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()

    folders = folder_result.get("files", [])
    if not folders:
        raise FileNotFoundError(f"Папка '{FOLDER_NAME}' не найдена")

    folder_id = folders[0]["id"]

    # Найти файл в папке
    files_result = service.files().list(
        q=f"name='{FILE_NAME}' and '{folder_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()

    files = files_result.get("files", [])
    if not files:
        raise FileNotFoundError(f"Файл '{FILE_NAME}' не найден в папке '{FOLDER_NAME}'")

    file_id = files[0]["id"]

    # Скачать файл
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    # Сохранить локально
    with open("input.xlsx", "wb") as f:
        f.write(file_data.getvalue())

    print("✅ Файл скачан: input.xlsx")


if __name__ == "__main__":
    download_file()
