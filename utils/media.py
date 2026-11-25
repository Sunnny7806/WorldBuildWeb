import os
import uuid
import base64
import streamlit as st
from utils.constants import get_upload_dir

#BU KOD UYGULAMAYA YÜKLENEN RESİMLERİ KAYDEDİYOR.

def saveUploadedImage(uploaded_file) -> str:
    """Yüklenen görsel dosyasını uploads klasörüne kaydeder ve dosya yolunu döner."""
    if not uploaded_file:
        return ""
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    filepath = os.path.join(get_upload_dir(), filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath


@st.cache_data
def imageToDataUri(path: str, mtime: float) -> str:
    """Görseli HTML bileşeninde göstermek için base64 Data URI formatına çevirir."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].replace(".", "").lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{b64}"
