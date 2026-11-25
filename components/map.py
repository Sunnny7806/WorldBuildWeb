import os
import streamlit as st
import streamlit.components.v1 as components
from utils.constants import BASE_DIR, TYPE_ICONS, goTo
from utils.media import imageToDataUri

# Özel HTML/JS harita bileşeni
_mapComponent = components.declare_component(
    "interactive_map",
    path=os.path.join(BASE_DIR, "components", "interactive_map"),
)


def interactiveMap(image_path: str, pins_data: list, key: str):
    """
    Harita görselini ve pinlerini çizer.
    - Pine tıklanırsa doğrudan o sayfaya yönlendirir.
    - Haritaya tıklanırsa koordinatları (x, y) session_state içine kaydeder.
    """
    pendingKey = f"{key}_pending"
    lastKey = f"{key}_last_ts"

    pins = [
        {
            "x": p.x,
            "y": p.y,
            "label": p.label or e.name,
            "name": e.name,
            "icon": TYPE_ICONS.get(e.entity_type, "📍"),
        }
        for p, e in pins_data
    ]
    preview = st.session_state.get(pendingKey)

    result = _mapComponent(
        img=imageToDataUri(image_path, os.path.getmtime(image_path)),
        pins=pins,
        preview=list(preview) if preview else None,
        key=key,
        default=None,
    )

    # Aynı tıklamayı birden fazla kez işlemeyi önleme
    if not result or result.get("ts") == st.session_state.get(lastKey):
        return
    st.session_state[lastKey] = result["ts"]

    if result["action"] == "goto":
        st.session_state.pop(pendingKey, None)
        goTo(result["name"])
        st.rerun()
    elif result["action"] == "click":
        st.session_state[pendingKey] = (result["x"], result["y"])
        st.rerun()
