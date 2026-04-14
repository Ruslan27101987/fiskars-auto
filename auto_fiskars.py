import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ===== настройки =====
EXCEL_FILE = "input.xlsx"
EMAIL_RECEIVER = "supplierpricelist@comfy.ua, ruslan.himich@gmail.com"

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def process_file(file_path):
    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    df["Артикул"] = (
        df["Артикул"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )
    df["Цена"] = pd.to_numeric(df["Цена"], errors="coerce")
    df["Количество"] = pd.to_numeric(df["Количество"], errors="coerce").fillna(0)

    df = df[df["Артикул"].ne("") & df["Цена"].notna()].copy().reset_index(drop=True)

    def calc_avbt(qty):
        if qty == 0:
            return 0
        elif qty <= 20:
            return 1
        return 2

    today = datetime.now().strftime("%Y%m%d")
    now_time = datetime.now().strftime("%H%M%S")

    out = pd.DataFrame(index=df.index)

    out["vendor_id"] = "VN72123277"
    out["price_date"] = today
    out["vendor_cat"] = df["Раздел"]
    out["vendor_item_id"] = df["Артикул"]
    out["vendor_item_name"] = df["Название (UA)"]
    out["brand"] = df["Бренд"]
    out["barcode"] = df["Штрихкод"]
    out["UCGFEA"] = df["Код УКТ ВЭД"]
    out["warranty"] = df["Гарантийный срок, мес."]
    out["qty"] = ""
    out["price"] = (df["Цена"] * 0.75).round(2)
    out["price_RIP"] = df["Цена"]
    out["avbt"] = df["Количество"].apply(calc_avbt)
    out["CurrencyId"] = "UAH"
    out["Part_number"] = df["Артикул"]

    if "Country_of_origin" in df.columns:
        out["Country_of_origin"] = df["Country_of_origin"]
    elif "Country of origin" in df.columns:
        out["Country_of_origin"] = df["Country of origin"]
    else:
        out["Country_of_origin"] = ""

    out["PDV_rate"] = 20

    out = out[
        [
            "vendor_id",
            "price_date",
            "vendor_cat",
            "vendor_item_id",
            "vendor_item_name",
            "brand",
            "barcode",
            "UCGFEA",
            "warranty",
            "qty",
            "price",
            "price_RIP",
            "avbt",
            "CurrencyId",
            "Part_number",
            "Country_of_origin",
            "PDV_rate",
        ]
    ]

    filename = f"VN72123277_{today}_{now_time}.csv"

    csv_text = out.to_csv(
        sep=";",
        index=False,
        lineterminator="\r\n",
    )

    with open(filename, "wb") as f:
        f.write(csv_text.encode("utf-8"))

    return filename


def send_email(file_path):
    recipients = [email.strip() for email in EMAIL_RECEIVER.split(",")]

    msg = EmailMessage()
    msg["Subject"] = "Fiskars price list"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(recipients)

    msg.set_content("Автоматическая отправка прайса")

    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(file_path),
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg, to_addrs=recipients)


if __name__ == "__main__":
    csv_file = process_file(EXCEL_FILE)
    send_email(csv_file)
    print("Готово 🚀")