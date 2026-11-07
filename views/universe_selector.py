import streamlit as st
from utils.universe import list_universes, create_universe
from database import set_active_universe, get_engine

def render_universe_selector():
    """Kullanıcının evren seçtiği veya yeni evren yarattığı açılış ekranı."""
    st.title("🌌 RPG WorldBuilding — Evren Seçimi")
    st.write("Yönetmek istediğiniz evrene giriş yapın veya yepyeni bir dünya yaratın.")
    st.divider()

    universes = list_universes()

    col_left, col_right = st.columns([2,1])

    #SOL SÜTUN: mevcut evrenler listesi
    with col_left:
        st.subheader("🪐 Kayıtlı Evrenleriniz")
        if not universes:
            st.info("Henüz kayıtlı bir evreniniz yok. Sağ taraftan ilk evreninizi oluşturun!")
        else:
            for u_name in universes:
                with st.container(border=True):
                    c1,c2 = st.columns([3,1], vertical_alignment="center")
                    c1.markdown(f"### 📜 {u_name}")
                    if c2.button("🚀 Giriş Yap", key=f"enter_{u_name}", use_container_width=True):
                    # Evreni aktif yap ve motorunu kur
                        st.session_state["active_universe"] = u_name
                        set_active_universe(u_name)
                        get_engine(u_name)
                        st.query_params.clear()
                        st.rerun()

    #SAĞ SÜTUN: Evren oluşturma sütunu
    with col_right:
        st.subheader("✨ Yeni Evren Yarat")
        with st.form("form_create_universe"):
            new_u_name = st.text_input("Evren Adı *", placeholder="Örn: Faerun, Ruby")
            submitted = st.form_submit_button("Oluştur ve Giriş Yap", use_container_width=True)

            if submitted:
                new_u_name = new_u_name.strip()
                if not new_u_name:
                    st.error("Lütfen bir evren adı giriniz.")
                elif new_u_name in universes:
                    st.error(f"{new_u_name} adında bir evren zaten var.")
                else:
                    if create_universe(new_u_name):
                        st.session_state["active_universe"] = new_u_name
                        set_active_universe(new_u_name)
                        get_engine(new_u_name)
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("Evren Oluşturulamadı.")



















