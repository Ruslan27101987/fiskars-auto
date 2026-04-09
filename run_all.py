import subprocess

print("🚀 Запуск процесса...")

print("📥 Скачиваем файл с Google Drive...")
subprocess.run(["python3", "drive_loader.py"], check=True)

print("⚙️ Обрабатываем файл и отправляем на почту...")
subprocess.run(["python3", "auto_fiskars.py"], check=True)

print("✅ Готово!")