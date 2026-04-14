from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "service_account.json"
FOLDER_NAME = "Fiskars_Input"


def test_connection():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    service = build("drive", "v3", credentials=creds)

    # 1) Ищем папку по имени
    folder_results = service.files().list(
        q=(
            f"name = '{FOLDER_NAME}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and trashed = false"
        ),
        fields="files(id, name)"
    ).execute()

    folders = folder_results.get("files", [])

    if not folders:
        print("❌ Папка Fiskars_Input не найдена")
        return

    folder_id = folders[0]["id"]
    print(f"✅ Папка найдена: {folders[0]['name']} | ID: {folder_id}")

    # 2) Смотрим, что внутри
    file_results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType)"
    ).execute()

    files = file_results.get("files", [])

    if not files:
        print("❌ В папке файлов нет")
    else:
        print("✅ Файлы найдены:")
        for f in files:
            print(f"{f['name']} | {f['mimeType']} | {f['id']}")


if __name__ == "__main__":
    test_connection()