import subprocess
import sys
from threading import Thread

def run_app(command):
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    commands = [
        "python ./main/app.py",
        "python ./Aeroconnect/main.py",
        "python ./TelecomNetPlanes/main.py",
        "python ./TelecomNetAgendamiento/main.py",
        "python ./TelecomNetTecnico/main.py",
        "python ./GasComunal/main.py"
    ]

    threads = []
    for cmd in commands:
        thread = Thread(target=run_app, args=(cmd,))
        thread.start()
        threads.append(thread)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Deteniendo todas las aplicaciones...")
        sys.exit(0)