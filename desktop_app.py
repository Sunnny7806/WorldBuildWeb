import sys
import time
import socket
import subprocess
import os
import webview

#BİR APP OLARAK ÇALIŞMASINI SAĞLAYAN KOD.

def is_port_open(port=8501):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_app():
    # Proje dizininde olduğumuzdan emin olalım
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # 1. Streamlit sunucusunu tamamen penceresiz olarak başlat
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.headless=true",
        "--server.port=8501"
    ]
    
    server_process = subprocess.Popen(
        cmd,
        cwd=project_dir,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Sunucunun portu dinlemeye başlamasını bekle (en fazla 10 saniye)
    for _ in range(50):
        if is_port_open(8501):
            break
        time.sleep(0.2)

    try:
        # 2. Bağımsız masaüstü penceresini oluştur
        window = webview.create_window(
            title="RPG Wiki",
            url="http://localhost:8501",
            width=1280,
            height=800,
            resizable=True
        )

        # 3. Pencereyi aç (Kullanıcı pencereyi kapatana kadar çalışır)
        webview.start()

    finally:
        # 4. Pencere kapandığında Streamlit sunucusunu tamamen öldür
        try:
            server_process.terminate()
            server_process.wait(timeout=3)
        except Exception:
            server_process.kill()

if __name__ == "__main__":
    start_app()
