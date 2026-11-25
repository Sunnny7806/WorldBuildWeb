import streamlit as st
from database import set_active_universe
from views.universe_selector import render_universe_selector
from views.sidebar import render_sidebar
from views.home import render_home_view
from views.entity_detail import render_entity_detail_view
from views.create import render_create_view
from views.dm_screen import render_dm_screen

#TÜM FRONTEND KODLARININ UYGULAMADA GÖRÜNMESİNİ SAĞLAYAN THE KOD.

# Streamlit sayfa yapılandırması
st.set_page_config(page_title="RPG Wiki", page_icon="📜", layout="wide")

active_universe = st.session_state.get("active_universe")

if not active_universe:
    render_universe_selector()
else:
    set_active_universe(active_universe)
    # 1. Sol kenar çubuğunu çiz
    render_sidebar()

    # 2. Sayfa yönlendirmesi (Routing)
    page = st.query_params.get("page")

    if page == "__new__":
        render_create_view()
    elif page == "__dm_screen__":
        render_dm_screen()
    elif page:
        render_entity_detail_view(page)
    else:
        render_home_view()
