import os
import streamlit as st
from worldManager import WorldManager
from utils.constants import TYPE_ICONS, get_upload_dir
from components.map import interactiveMap

#BURASI APP İLK AÇILDIĞINDA KARŞIMIZA ÇIKAN DÜNYA HARİTASI OLAN EKRANIN KODLARI.


def render_home_view():
    """Ana sayfayı (Sayaçlar, Dünya Haritası ve Pin Yönetimi) çizer."""
    st.title("📜 RPG Wiki")
    st.write("Soldan bir sayfa seçebilir ya da dünya haritasından şehirlere gidebilirsiniz.")

    allEntities = WorldManager.get_all_entities()
    cols = st.columns(len(TYPE_ICONS))
    for col, (t, icon) in zip(cols, TYPE_ICONS.items()):
        col.metric(f"{icon} {t.capitalize()}", sum(1 for e in allEntities if e.entity_type == t))

    st.divider()
    st.subheader("🗺️ Bilinen Dünya Haritası")

    world_map_path = os.path.join(get_upload_dir(), "world_map.png")
    WORLD_PENDING = "world_map_pending"

    if os.path.exists(world_map_path):
        world_pins = WorldManager.get_map_pins(map_type="world")
        interactiveMap(world_map_path, world_pins, key="world_map")
        st.caption("💡 İpucu: Harita üzerinde bir yere **tıklayarak** doğrudan o konuma şehir pini yerleştirebilirsiniz.")
    else:
        st.info("Henüz bir dünya haritası yüklenmemiş. Aşağıdaki menüden bir harita görseli yükleyin.")

    # Haritada bir nokta seçildiyse:
    preview = st.session_state.get(WORLD_PENDING)
    if preview:
        clicked_x, clicked_y = preview
        with st.container():
            st.success(f"🎯 Haritada bir nokta seçtiniz! (X: %{clicked_x}, Y: %{clicked_y})")

            tab_exist, tab_new = st.tabs(["🏰 Var Olan Şehri Yerleştir", "✨ Yeni Şehir Oluştur & Yerleştir"])

            with tab_exist:
                all_cities = [e for e in allEntities if e.entity_type == "location"]
                if not all_cities:
                    st.info("Kayıtlı şehir bulunmuyor. Yan taraftaki 'Yeni Şehir Oluştur' sekmesinden ekleyebilirsiniz.")
                else:
                    col_c1, col_c2 = st.columns([3, 1])
                    selected_city = col_c1.selectbox("Bu noktaya hangi şehir yerleştirilsin?", options=all_cities, format_func=lambda x: x.name, key="sel_exist_city")
                    custom_lbl = col_c1.text_input("Özel Etiket (İsteğe bağlı)", value="", key="lbl_exist_city")

                    if col_c2.button("📌 Pini Buraya Kaydet", key="btn_save_exist_city", use_container_width=True):
                        WorldManager.add_map_pin(
                            map_type="world",
                            target_entity_id=selected_city.id,
                            x=float(clicked_x),
                            y=float(clicked_y),
                            label=custom_lbl
                        )
                        st.session_state.pop(WORLD_PENDING, None)
                        st.rerun()

            with tab_new:
                st.caption("Temel bilgileri girerek hızlıca şehri oluşturun ve haritaya yerleştirin:")
                nc1, nc2 = st.columns(2)
                new_city_name = nc1.text_input("Şehir Adı *", key="new_city_name", placeholder="Örn: Asterfall")
                new_ruler = nc2.text_input("Yönetici (İsteğe bağlı)", key="new_city_ruler", placeholder="Örn: Kral Alden")
                nc3, nc4 = st.columns(2)
                new_pop = nc3.text_input("Nüfus (İsteğe bağlı)", key="new_city_pop", placeholder="Örn: 25.000")
                new_climate = nc4.text_input("İklim (İsteğe bağlı)", key="new_city_climate", placeholder="Örn: Soğuk, Dağlık")

                btn_col1, btn_col2 = st.columns([2, 1])
                if btn_col1.button("🚀 Şehri Oluştur ve Pini Yerleştir", key="btn_quick_create_city", type="primary", use_container_width=True):
                    new_city_name = new_city_name.strip()
                    if not new_city_name:
                        st.error("Lütfen bir şehir adı girin.")
                    elif WorldManager.getEntityByName(new_city_name):
                        st.error(f"'{new_city_name}' adında bir sayfa zaten var.")
                    else:
                        new_loc = WorldManager.create_location(
                            name=new_city_name,
                            population=new_pop,
                            religion="",
                            climate=new_climate,
                            ruler=new_ruler,
                            aliases="",
                            content_md=f"# {new_city_name}\n\nBu şehir harita üzerinden hızlıca oluşturuldu."
                        )
                        if new_loc:
                            WorldManager.add_map_pin(
                                map_type="world",
                                target_entity_id=new_loc.id,
                                x=float(clicked_x),
                                y=float(clicked_y),
                                label=""
                            )
                            st.session_state.pop(WORLD_PENDING, None)
                            st.rerun()

                if btn_col2.button("❌ İptal", key="btn_cancel_quick_city", use_container_width=True):
                    st.session_state.pop(WORLD_PENDING, None)
                    st.rerun()

    # Harita Görseli ve Pin Yönetimi Menüsü
    with st.expander("⚙️ Harita Görselini Değiştir / Pinleri Yönet"):
        t1, t2 = st.tabs(["🗺️ Harita Görseli", "🗑️ Pinleri Sil"])
        with t1:
            new_map = st.file_uploader("Yeni Dünya Haritası Yükle", type=["png", "jpg", "jpeg", "webp"], key="up_world")
            if new_map and st.button("Haritayı Kaydet"):
                with open(world_map_path, "wb") as f:
                    f.write(new_map.getbuffer())
                st.success("Harita kaydedildi!")
                st.rerun()
        with t2:
            cur_pins = WorldManager.get_map_pins(map_type="world")
            if not cur_pins:
                st.caption("Henüz kayıtlı pin yok.")
            else:
                for p, ent in cur_pins:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🏰 **{ent.name}** — (X: %{p.x}, Y: %{p.y})")
                    if c2.button("Sil", key=f"del_{p.id}"):
                        WorldManager.delete_map_pin(p.id)
                        st.rerun()
