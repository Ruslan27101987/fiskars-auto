import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SERVICE_ACCOUNT_FILE = "/etc/secrets/service_account.json"
FOLDER_NAME = "Fiskars_Input"
FILE_NAME = "input.xlsx"


def download_file():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    # Найти папку
    folder = service.files().list(
        q=f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()["files"][0]

    folder_id = folder["id"]

    # Найти файл
    files = service.files().list(
        q=f"name='{FILE_NAME}' and '{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()["files"]

    if not files:
        print("❌ Файл не найден")
        return

    file_id = files[0]["id"]

    # Скачать файл
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    # Сохранить
    with open("input.xlsx", "wb") as f:
        f.write(file_data.getvalue())

    print("✅ Файл скачан: input.xlsx")


if __name__ == "__main__":
    download_file()
