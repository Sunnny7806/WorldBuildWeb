import os
import streamlit as st
from worldManager import WorldManager
from backlinks import BacklinkManager
from utils.constants import TYPE_ICONS, goTo, renderLinks, getDetails
from utils.media import saveUploadedImage

# Modüler alt bileşenler
from components.character_sheet import render_character_sheet
from components.monster_stat_block import render_monster_stat_block
from components.faction_view import render_faction_view
from components.inventory_view import render_district_inventory, render_item_transfer
from components.city_map import render_city_map

def render_entity_detail_view(name: str):
    """Bir varlığın detay sayfasını, düzenleme modunu ve ilgili alt bileşenlerini çizer."""
    entity = WorldManager.getEntityByName(name)
    if not entity:
        st.error(f"'{name}' adında bir sayfa yok.")
        return

    icon = TYPE_ICONS.get(entity.entity_type, "📄")
    st.title(f"{icon} {entity.name}")
    if entity.aliases:
        st.caption(f"Diğer adları: {entity.aliases}")

    left, right = st.columns([2.5, 1])

    # SAĞ SÜTUN: Portre + Temel Bilgiler + Alt Mekanlar + Bağlantılar
    with right:
        img_path = getattr(entity, 'image_path', '')
        if img_path and os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

        st.subheader("Bilgiler")
        for label, value in getDetails(entity).items():
            if value:
                st.markdown(f"**{label}:** {value}")

        # Eğer bu bir District ise bağlı olduğu Şehir butonu:
        if entity.district and entity.district.parent_location_id:
            parent_loc = WorldManager.getEntityById(entity.district.parent_location_id)
            if parent_loc:
                st.subheader("📍 Bağlı Olduğu Şehir")
                st.button(f"🏰 {parent_loc.name}", key="btn_parent_loc", on_click=goTo, args=(parent_loc.name,))

        # Eğer bu bir Karakter ise ve bir loncaya bağlıysa:
        if entity.character and entity.character.faction_id:
            parent_faction = WorldManager.getEntityById(entity.character.faction_id)
            if parent_faction:
                st.subheader("🛡️ Bağlı Olduğu Lonca")
                st.button(f"🛡️ {parent_faction.name}", key="btn_char_faction", on_click=goTo, args=(parent_faction.name,), use_container_width=True)

        # Eğer bu bir Şehir ise içindeki mekanların butonları:
        if entity.location:
            sub_districts = WorldManager.getDistrictsOfLocation(entity.id)
            if sub_districts:
                st.subheader("🏘️ Bölgeler & Mekanlar")
                for dist in sub_districts:
                    st.button(f"🍺 {dist.name}", key=f"dist_{dist.id}", on_click=goTo, args=(dist.name,))

        st.subheader("Bu sayfaya bağlantılar")
        backlinks = BacklinkManager.getBacklinks(entity.id)
        if not backlinks:
            st.caption("Henüz yok.")
        for b in backlinks:
            st.button(b.name, key=f"bl_{b.id}", on_click=goTo, args=(b.name,))

    # SOL SÜTUN: İçerik / Düzenleme ve Modüler Alt Bileşenler
    with left:
        if st.toggle("✏️ Düzenle", key=f"edit_{entity.id}"):
            newname = st.text_area("İsim",value=entity.name or "", height=20)
            newaliaes = st.text_area("Takma Adlar",value=entity.aliases or "", height=20)
            newText = st.text_area("İçerik", value=entity.content_md or "", height=300)

            st.markdown("##### 🖼️ Görsel Ayarları")
            new_img = st.file_uploader(
                "Görseli Değiştir / Yükle",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"upload_edit_{entity.id}"
            )
            remove_img = False
            if getattr(entity, 'image_path', ''):
                remove_img = st.checkbox("Mevcut resmi kaldır", key=f"rm_{entity.id}")

            if st.button("💾 Kaydet"):
                WorldManager.updateEntity(entity.id, name=newname, aliases=newaliaes)
                WorldManager.updateEntity(entity.id, )
                BacklinkManager.saveContent(entity.id, newText)
                st.query_params["page"] = newname
                if new_img:
                    saved_path = saveUploadedImage(new_img)
                    WorldManager.updateEntity(entity.id, image_path=saved_path)
                elif remove_img:
                    WorldManager.updateEntity(entity.id, image_path="")
                st.rerun()
        else:
            names = {e.name for e in WorldManager.get_all_entities()}
            content = entity.content_md or "_Bu sayfa henüz boş._"
            st.markdown(renderLinks(content, names), unsafe_allow_html=True)

        # 👥 Lonca (Faction) Özel Görünümü & Kadro Jeneratörü
        if entity.faction:
            render_faction_view(entity)

        # 📊 Karakter Kâğıdı (Character Sheet) & Canlı Envanter
        if entity.character:
            render_character_sheet(entity)

        # 📦 Mekan/Dükkan Envanteri (Bulunan / Satılan Eşyalar)
        if entity.district:
            render_district_inventory(entity)

        # 🔄 Eşya Sahipliği ve Mekan Yönetimi
        if entity.item:
            render_item_transfer(entity)

        # 🐉 Canavar Stat Bloğu & Sahneye Sürme
        if entity.monster:
            render_monster_stat_block(entity)

        # 🗺️ Şehir Haritası (Eğer sayfa bir Şehir ise)
        if entity.location:
            render_city_map(entity)

        with st.expander("🗑️ Sayfayı sil"):
            st.warning("Bu işlem geri alınamaz.")
            if st.button("Evet, sil", type="primary"):
                WorldManager.deleteEntity(entity.id)
                st.query_params.clear()
                st.rerun()
