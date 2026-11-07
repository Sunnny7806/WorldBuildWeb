import os
import streamlit as st
from worldManager import WorldManager
from utils.constants import TYPE_ICONS, goTo
from database import get_active_universe

# SOLDAKİ KARTLARIN VE ARAMA ÇUBUĞUNUN OLDUĞU KISMIN KODLARI.


def render_sidebar():
    """Sol kenar çubuğunu (Arama, Kompakt Kategori Filtreleri, Liste ve Yeni Sayfa Butonu) çizer."""
    with st.sidebar:
        # Kompakt stil CSS (Yazıları ve butonları küçülterek yer tasarrufu sağlar)
        st.markdown(
            """
            <style>
            /* Kompakt filtre hapları (pills) */
            div[data-testid="stPills"] button {
                padding: 1px 7px !important;
                font-size: 11px !important;
                min-height: 24px !important;
                line-height: 1.1 !important;
            }
            /* Sol menü varlık butonlarını daha zarif ve kompakt yapar */
            div[data-testid="stSidebar"] div.stButton > button {
                padding: 3px 8px !important;
                font-size: 13px !important;
                min-height: 32px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        active_u = get_active_universe()
        c_u1, c_u2 = st.columns([2, 1], vertical_alignment="center")
        c_u1.caption(f"🪐 Evren: **{active_u}**")
        if c_u2.button("🔄 Değiştir", use_container_width=True):
            st.session_state.pop("active_universe", None)
            st.query_params.clear()
            st.rerun()

        # Aşama 4: DM Masası (Karşılaşma & Canavarlar) Hızlı Giriş Butonu
        if st.button("⚔️ DM Masası & Savaş", type="primary", use_container_width=True):
            st.query_params["page"] = "__dm_screen__"
            st.rerun()

        st.divider()
        st.title("📜 RPG Wiki")
        keyword = st.text_input("🔍 Ara", label_visibility="collapsed", placeholder="🔍 Ara...")
        entities = WorldManager.search(keyword) if keyword else WorldManager.get_all_entities()

        # Tüm Varlık Türleri İçin Kompakt Kategori Filtresi
        filter_options = [
            "Tümü", "⭐ Oyuncu", "🎭 NPC", "🐉 Canavar", "🏰 Şehir", "🍺 Mekan", "🛡️ Lonca", "💎 Eşya", "⚡ Tanrı"
        ]
        selected_filter = st.pills(
            "Filtre",
            options=filter_options,
            default="Tümü",
            label_visibility="collapsed",
            key="sb_entity_pills"
        )

        if selected_filter == "⭐ Oyuncu":
            entities = [e for e in entities if e.character and getattr(e.character, "is_player", False)]
        elif selected_filter == "🎭 NPC":
            entities = [e for e in entities if e.character and not getattr(e.character, "is_player", False)]
        elif selected_filter == "🐉 Canavar":
            entities = [e for e in entities if e.entity_type == "monster"]
        elif selected_filter == "🏰 Şehir":
            entities = [e for e in entities if e.entity_type == "location"]
        elif selected_filter == "🍺 Mekan":
            entities = [e for e in entities if e.entity_type == "district"]
        elif selected_filter == "🛡️ Lonca":
            entities = [e for e in entities if e.entity_type == "faction"]
        elif selected_filter == "💎 Eşya":
            entities = [e for e in entities if e.entity_type == "item"]
        elif selected_filter == "⚡ Tanrı":
            entities = [e for e in entities if e.entity_type == "god"]

        st.caption(f"Toplam: **{len(entities)}** kayıt")

        for e in sorted(entities, key=lambda x: x.name):
            col_icon, col_name = st.columns([1, 4], vertical_alignment="center")

            with col_icon:
                img_path = getattr(e, 'image_path', '')
                if img_path and os.path.exists(img_path):
                    st.image(img_path, width=28)
                else:
                    icon = "⭐" if (e.character and getattr(e.character, "is_player", False)) else TYPE_ICONS.get(e.entity_type, "📄")
                    st.markdown(f"<div style='font-size:18px; text-align:center;'>{icon}</div>", unsafe_allow_html=True)

            with col_name:
                display_name = f"⭐ {e.name}" if (e.character and getattr(e.character, "is_player", False)) else e.name
                st.button(display_name, key=f"sb_{e.id}", on_click=goTo, args=(e.name,), use_container_width=True)

        st.divider()
        st.button("➕ Yeni sayfa", on_click=goTo, args=("__new__",), use_container_width=True)
