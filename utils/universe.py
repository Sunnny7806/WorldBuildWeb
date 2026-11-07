import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIVERSE_DIR = os.path.join(BASE_DIR, "universes")
os.makedirs(UNIVERSE_DIR, exist_ok=True)

def get_universe_dirs(universe_name:str):
    """Bir evrenin veritabanı dosya yolunu ve uploads klasorünü döner."""
    u_dir = os.path.join(UNIVERSE_DIR, universe_name)
    db_path = os.path.join(u_dir, "wiki.db")
    upload_dir = os.path.join(u_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    return db_path, upload_dir

def list_universes() -> list:
    """universes/ dosyası altındaki tüm evrenleri bir liste halinde döner."""
    if not os.path.exists(UNIVERSE_DIR):
        return []
    return[
        d for d in os.listdir(UNIVERSE_DIR)
        if os.path.isdir(os.path.join(UNIVERSE_DIR, d))
    ]

def create_universe(universe_name: str) -> bool:
    """Yeni bir evren klasörü ve upploads dizini oluşturur."""
    universe_name = universe_name.strip()
    if not universe_name:
        return False

    u_dir = os.path.join(UNIVERSE_DIR, universe_name)
    if os.path.exists(u_dir):
        return False

    upload_dir = os.path.join(u_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    return True

