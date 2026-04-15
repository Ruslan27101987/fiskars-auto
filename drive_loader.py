import io
import os

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "/etc/secrets/service_account.json")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
FILE_NAME = os.getenv("FILE_NAME", "input.xlsx")


def download_file():
    if not DRIVE_FOLDER_ID:
        raise ValueError("❌ DRIVE_FOLDER_ID не найден")

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise ValueError(f"❌ Не найден файл ключа: {SERVICE_ACCOUNT_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    print("🔍 Ищем файл на Google Drive...")

    results = service.files().list(
        q=f"name='{FILE_NAME}' and '{DRIVE_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if not files:
        raise FileNotFoundError(f"❌ Файл {FILE_NAME} не найден")

    file_id = files[0]["id"]

    print(f"📥 Найден файл: {FILE_NAME}")

    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"⬇️ {int(status.progress() * 100)}%")

    with open(FILE_NAME, "wb") as f:
        f.write(file_data.getvalue())

    print(f"✅ Файл скачан: {FILE_NAME}")


if __name__ == "__main__":
    download_file()