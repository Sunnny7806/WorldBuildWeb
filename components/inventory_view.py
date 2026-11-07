import streamlit as st
from worldManager import WorldManager
from utils.constants import goTo

def render_district_inventory(entity):
    """Mekan veya dükkanda bulunan / satılan eşyaları listeler."""
    if not entity.district:
        return

    st.divider()
    st.subheader("📦 Bu Mekandaki Eşyalar & Satılık Mallar")
    place_items = WorldManager.get_location_inventory(entity.id)
    if place_items:
        for p_item in place_items:
            st.button(f"💎 {p_item.name}", key=f"p_item_{p_item.id}", on_click=goTo, args=(p_item.name,))
    else:
        st.caption("Burada henüz kayıtlı bir eşya veya satılık mal yok.")


def render_item_transfer(entity):
    """Bir eşyanın sahibini (karakter) veya bulunduğu mekanı (district) interaktif değiştirmeyi sağlar."""
    if not entity.item:
        return

    st.divider()
    with st.expander("🔄 Eşyanın Sahibini veya Bulunduğu Yeri Değiştir"):
        all_chars = [e for e in WorldManager.get_all_entities() if e.entity_type == "character"]
        all_districts = [e for e in WorldManager.get_all_entities() if e.entity_type == "district"]

        # Mevcut sahibin ve mekanın seçili gelmesi için indeks bulma
        cur_owner = WorldManager.getEntityById(entity.item.owner_id) if entity.item.owner_id else None
        owner_opts = [None] + all_chars
        owner_idx = owner_opts.index(cur_owner) if cur_owner in owner_opts else 0

        cur_loc = WorldManager.getEntityById(entity.item.location_id) if entity.item.location_id else None
        loc_opts = [None] + all_districts
        loc_idx = loc_opts.index(cur_loc) if cur_loc in loc_opts else 0

        c_own, c_loc = st.columns(2)
        new_owner = c_own.selectbox(
            "Eşyanın Sahibi (Karakter):", 
            options=owner_opts, 
            index=owner_idx, 
            format_func=lambda x: "— Sahipsiz —" if x is None else x.name,
            key=f"sel_own_{entity.id}"
        )
        new_place = c_loc.selectbox(
            "Bulunduğu Dükkan/Mekan:", 
            options=loc_opts, 
            index=loc_idx, 
            format_func=lambda x: "— Belirtilmemiş —" if x is None else x.name,
            key=f"sel_place_{entity.id}"
        )

        if st.button("💾 Sahiplik / Konum Bilgisini Güncelle", key=f"btn_upd_item_{entity.id}", type="primary", use_container_width=True):
            o_id = new_owner.id if new_owner else None
            l_id = new_place.id if new_place else None
            WorldManager.updateEntity(entity.id, owner_id=o_id, location_id=l_id)
            st.success("Eşya bilgileri güncellendi!")
            st.rerun()
