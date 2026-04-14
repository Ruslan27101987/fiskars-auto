import os

folder = os.getcwd()

for file in os.listdir(folder):
    if file.endswith(".csv") or file == "input.xlsx":
        try:
            os.remove(file)
            print(f"Удален: {file}")
        except Exception as e:
            print(f"Ошибка удаления {file}: {e}")

print("Очистка завершена 🧹")