import io
import os
import json

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
FILE_NAME = os.getenv("FILE_NAME", "input.xlsx")


def download_file():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT_JSON не найден в .env")

    # превращаем строку JSON в dict
    service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    print("🔍 Ищем файл на Google Drive...")

    # ищем файл в папке
    results = service.files().list(
        q=f"name='{FILE_NAME}' and '{DRIVE_FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if not files:
        print("❌ Файл не найден")
        return

    file_id = files[0]["id"]

    print(f"📥 Найден файл: {FILE_NAME}")

    # скачивание
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"⬇️ {int(status.progress() * 100)}%")

    with open("input.xlsx", "wb") as f:
        f.write(file_data.getvalue())

    print("✅ Файл скачан: input.xlsx")


if __name__ == "__main__":
    download_file()