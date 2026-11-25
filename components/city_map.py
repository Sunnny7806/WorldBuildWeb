import os
import streamlit as st
from worldManager import WorldManager
from utils.media import saveUploadedImage
from components.map import interactiveMap

def render_city_map(entity):
    """Şehir (Location) için interaktif harita, pin tıklama mekanizması ve harita ayarlarını render eder."""
    if not entity.location:
        return

    st.divider()
    st.subheader(f"🗺️ {entity.name} Şehir Haritası")

    city_map_path = getattr(entity.location, "map_image_path", "")
    cityMapKey = f"city_map_{entity.id}"
    cityPendingKey = f"{cityMapKey}_pending"

    if city_map_path and os.path.exists(city_map_path):
        city_pins = WorldManager.get_map_pins(map_type="location", location_id=entity.id)
        interactiveMap(city_map_path, city_pins, key=cityMapKey)
        st.caption("💡 İpucu: Şehir haritası üzerinde bir yere **tıklayarak** doğrudan o konuma mekan pini yerleştirebilirsiniz.")
    else:
        st.caption("Bu şehrin henüz bir haritası yüklenmemiş. Aşağıdaki menüden yükleyebilirsiniz.")

    # Şehir Haritasında Bir Nokta Seçildiyse:
    city_preview = st.session_state.get(cityPendingKey)
    if city_preview:
        clicked_x, clicked_y = city_preview
        with st.container():
            st.success(f"🎯 Haritada bir nokta seçtiniz! (X: %{clicked_x}, Y: %{clicked_y})")

            tab_d_exist, tab_d_new = st.tabs(["🍺 Var Olan Mekanı Yerleştir", "✨ Yeni Mekan Oluştur & Yerleştir"])

            with tab_d_exist:
                city_districts = WorldManager.getDistrictsOfLocation(entity.id)
                if not city_districts:
                    st.info("Bu şehre bağlı kayıtlı mekan bulunmuyor. Yan taraftaki sekmeden hızlıca oluşturabilirsiniz.")
                else:
                    dc1, dc2 = st.columns([3, 1])
                    sel_dist = dc1.selectbox("Mekan Seçin:", options=city_districts, format_func=lambda x: x.name, key="sel_exist_dist")
                    dlbl = dc1.text_input("Özel Etiket (İsteğe bağlı)", key="lbl_exist_dist")
                    if dc2.button("📌 Pini Kaydet", key="btn_save_exist_dist", use_container_width=True):
                        WorldManager.add_map_pin(
                            map_type="location",
                            location_id=entity.id,
                            target_entity_id=sel_dist.id,
                            x=float(clicked_x),
                            y=float(clicked_y),
                            label=dlbl
                        )
                        st.session_state.pop(cityPendingKey, None)
                        st.rerun()

            with tab_d_new:
                st.caption(f"**{entity.name}** şehrine bağlı yeni bir mekan oluşturup hemen haritaya yerleştirin:")
                ndc1, ndc2 = st.columns(2)
                new_dist_name = ndc1.text_input("Mekan Adı *", key="new_dist_name", placeholder="Örn: Sarhoş Ejderha Hanı")
                new_dist_type = ndc2.text_input("Mekan Türü", key="new_dist_type", placeholder="Örn: Han/Taverna, Pazar")
                new_dist_owner = st.text_input("Sahibi / İşletmecisi (İsteğe bağlı)", key="new_dist_owner", placeholder="Örn: Barmen Bob")

                dbtn1, dbtn2 = st.columns([2, 1])
                if dbtn1.button("🚀 Mekanı Oluştur ve Pini Yerleştir", key="btn_quick_create_dist", type="primary", use_container_width=True):
                    new_dist_name = new_dist_name.strip()
                    if not new_dist_name:
                        st.error("Lütfen bir mekan adı girin.")
                    elif WorldManager.getEntityByName(new_dist_name):
                        st.error(f"'{new_dist_name}' adında bir sayfa zaten var.")
                    else:
                        new_dist = WorldManager.create_district(
                            name=new_dist_name,
                            parent_location_id=entity.id,
                            district_type=new_dist_type or "Mekan",
                            ruler_or_owner=new_dist_owner,
                            aliases="",
                            content_md=f"# {new_dist_name}\n\nBu mekan {entity.name} şehir haritasından hızlıca oluşturuldu."
                        )
                        if new_dist:
                            WorldManager.add_map_pin(
                                map_type="location",
                                location_id=entity.id,
                                target_entity_id=new_dist.id,
                                x=float(clicked_x),
                                y=float(clicked_y),
                                label=""
                            )
                            st.session_state.pop(cityPendingKey, None)
                            st.rerun()
                        else:
                            st.error("Mekan oluşturulamadı!")

                if dbtn2.button("❌ İptal", key="btn_cancel_quick_dist", use_container_width=True):
                    st.session_state.pop(cityPendingKey, None)
                    st.rerun()

    # Şehir Haritası Yükleme / Pin Yönetimi Paneli
    with st.expander("⚙️ Şehir Haritası Görselini Değiştir / Pinleri Yönet"):
        t1, t2 = st.tabs(["🖼️ Şehir Haritası Görseli", "🗑️ Pinleri Sil"])
        with t1:
            city_map_upload = st.file_uploader("Bu Şehrin Haritasını Yükle", type=["png", "jpg", "jpeg", "webp"], key="upload_city_map")
            if city_map_upload and st.button("Şehir Haritasını Kaydet"):
                saved_path = saveUploadedImage(city_map_upload)
                WorldManager.updateEntity(entity.id, map_image_path=saved_path)
                st.success("Şehir haritası kaydedildi!")
                st.rerun()

        with t2:
            cur_city_pins = WorldManager.get_map_pins(map_type="location", location_id=entity.id)
            if not cur_city_pins:
                st.caption("Henüz bu şehirde kayıtlı pin yok.")
            else:
                for cp, cent in cur_city_pins:
                    cc1, cc2 = st.columns([4, 1])
                    cc1.write(f"🍺 **{cent.name}** — (X: %{cp.x}, Y: %{cp.y})")
                    if cc2.button("Sil", key=f"del_cp_{cp.id}"):
                        WorldManager.delete_map_pin(cp.id)
                        st.rerun()
