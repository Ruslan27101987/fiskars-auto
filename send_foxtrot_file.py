import io
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "/etc/secrets/service_account.json")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

FILE_NAME = os.getenv("FOX_FILE_NAME", "Fiskars.xlsx")
EMAIL_RECEIVER = os.getenv("FOX_EMAIL_RECEIVER", "FTD_auto_price_loader@foxtrot.ua")


def download_file_by_name(file_name: str) -> tuple[bytes, str]:
    if not DRIVE_FOLDER_ID:
        raise ValueError("❌ DRIVE_FOLDER_ID не найден")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

    service = build("drive", "v3", credentials=creds)

    results = service.files().list(
        q=f"name='{file_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)",
        pageSize=10,
    ).execute()

    items = results.get("files", [])
    if not items:
        raise FileNotFoundError(f"❌ Файл '{file_name}' не найден")

    file_id = items[0]["id"]
    actual_name = items[0]["name"]

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    return fh.read(), actual_name


def send_file():
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD:
        raise ValueError("❌ EMAIL_SENDER или EMAIL_APP_PASSWORD не заданы")

    file_bytes, filename = download_file_by_name(FILE_NAME)

    msg = EmailMessage()
    msg["Subject"] = f"{filename}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content("Во вложении файл с Google Drive без изменений.")

    msg.add_attachment(
        file_bytes,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    print(f"✅ Файл {filename} отправлен на {EMAIL_RECEIVER}")


if __name__ == "__main__":
    send_file()