import io
import os
import uuid
import base64
import streamlit as st
from PIL import Image, ImageOps
from utils.constants import get_upload_dir

#BU KOD UYGULAMAYA YÜKLENEN RESİMLERİ KAYDEDİYOR.


def convert_image_to_webp(src, dest_path_no_ext: str, max_dim: int = 1600, quality: int = 90) -> str:
    """Görseli en-boy oranını ve keskinliğini koruyarak WebP formatında kaydeder."""
    out_path = f"{dest_path_no_ext}.webp"
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in ("P", "LA"):
            im = im.convert("RGBA")
        elif im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        if max(im.size) > max_dim:
            im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        im.save(out_path, format="WEBP", quality=quality, method=6)
    return out_path


def saveUploadedImage(uploaded_file, max_dim: int = 1600) -> str:
    """Yüklenen görsel dosyasını kaliteyi koruyarak WebP'ye dönüştürüp kaydeder."""
    if not uploaded_file:
        return ""
    stem = os.path.splitext(uploaded_file.name)[0]
    base_name = f"{uuid.uuid4().hex[:8]}_{stem}"
    dest_no_ext = os.path.join(get_upload_dir(), base_name)
    raw_bytes = uploaded_file.getbuffer()
    try:
        return convert_image_to_webp(io.BytesIO(raw_bytes), dest_no_ext, max_dim=max_dim)
    except Exception:
        ext = os.path.splitext(uploaded_file.name)[1] or ".png"
        fallback_path = f"{dest_no_ext}{ext}"
        with open(fallback_path, "wb") as f:
            f.write(raw_bytes)
        return fallback_path


def getWorldMapPath(upload_dir: str) -> str:
    """Önce optimize WebP, yoksa mevcut PNG dünya haritası yolunu döner."""
    webp_path = os.path.join(upload_dir, "world_map.webp")
    if os.path.exists(webp_path):
        return webp_path
    return os.path.join(upload_dir, "world_map.png")


def saveWorldMap(uploaded_file, upload_dir: str, max_dim: int = 2400) -> str:
    """Dünya haritasını yüksek çözünürlükte WebP olarak kaydeder."""
    dest_no_ext = os.path.join(upload_dir, "world_map")
    raw_bytes = uploaded_file.getbuffer()
    try:
        out_path = convert_image_to_webp(io.BytesIO(raw_bytes), dest_no_ext, max_dim=max_dim)
        old_png = os.path.join(upload_dir, "world_map.png")
        if os.path.exists(old_png):
            os.remove(old_png)
        return out_path
    except Exception:
        fallback_path = os.path.join(upload_dir, "world_map.png")
        with open(fallback_path, "wb") as f:
            f.write(raw_bytes)
        return fallback_path


@st.cache_data
def imageToDataUri(path: str, mtime: float) -> str:
    """Görseli HTML bileşeninde göstermek için base64 Data URI formatına çevirir."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].replace(".", "").lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{b64}"
