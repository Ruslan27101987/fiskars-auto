import subprocess
import sys

def run_script(script_name: str):
    print(f"\n🚀 Запуск: {script_name}")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result.returncode


def main():
    code = run_script("auto_fiskars.py")
    if code != 0:
        raise RuntimeError("❌ Ошибка в auto_fiskars.py")

    try:
        fox_code = run_script("send_foxtrot_file.py")
        if fox_code != 0:
            print("⚠️ send_foxtrot_file.py завершился с ошибкой")
    except Exception as e:
        print(f"⚠️ Ошибка Foxtrot: {e}")

    print("✅ Основной процесс завершён")


if __name__ == "__main__":
    main()