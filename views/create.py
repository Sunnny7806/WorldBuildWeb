import json
import streamlit as st
from worldManager import WorldManager
from backlinks import BacklinkManager
from utils.constants import TYPE_ICONS, goTo
from utils.media import saveUploadedImage

#BU KOD EVRENE YENİ BİR ENTİTY EKLEME EKRANININ FRONTEND İ VE BACKEND İ.


def render_create_view():
    """Yeni bir varlık (Karakter, Eşya, Şehir, Tanrı, Mekan, Lonca) oluşturma formunu çizer."""
    st.title("➕ Yeni sayfa")
    entityType = st.selectbox(
        "Tür", ["character", "item", "location", "god", "district", "faction", "monster"],
        format_func=lambda t: f"{TYPE_ICONS[t]} {t.capitalize()}",
    )

    with st.form("create"):
        name = st.text_input("İsim *")
        aliases = st.text_input("Takma adlar (virgülle ayır)")

        if entityType == "character":
            race = st.text_input("Irk")
            charClass = st.text_input("Sınıf")
            alignment = st.text_input("Yönelim")

            all_faction = [e for e in WorldManager.get_all_entities() if e.entity_type == "faction"]
            selected_faction = st.selectbox(
                "Bağlı Olduğu Lonca / Örgüt (İsteğe Bağlı)",
                options= [None] + all_faction,
                format_func=lambda x:"- Yok / Bağımsız - " if x  is None else x.name
                )
            faction_role = st.text_input("Loncadaki Rütbesi / Görevi (Örn: Usta Suikastçı)")

            # Aşama 3: PC (Oyuncu) vs NPC Seçimi
            is_player = st.checkbox("⭐ Bu bir Oyuncu Karakteri (PC) mi?", key="chk_is_player")
            player_name = ""
            level = 1
            hp_max = 10
            hp_current = 10
            armor_class = 10
            speed = "30 ft"
            stats_json = None
            spells_and_features = ""

            if is_player:
                col_p1, col_p2 = st.columns(2)
                player_name = col_p1.text_input("Oynayan Oyuncu Adı")
                level = col_p2.number_input("Seviye (Level)", min_value=1, max_value=20, value=1)

                col_hp1, col_hp2, col_ac, col_spd = st.columns(4)
                hp_max = int(col_hp1.number_input("Maksimum Can (HP)", min_value=1, value=10))
                hp_current = int(col_hp2.number_input("Mevcut Can (HP)", min_value=0, value=hp_max))
                armor_class = int(col_ac.number_input("Zırh Sınıfı (AC)", min_value=1, value=10))
                speed = col_spd.text_input("Hız (Speed)", value="30 ft")

                with st.expander("📊 Temel Yetenek Skorları (STR, DEX, CON, INT, WIS, CHA)"):
                    s1, s2, s3, s4, s5, s6 = st.columns(6)
                    val_str = s1.number_input("STR", min_value=1, max_value=30, value=10)
                    val_dex = s2.number_input("DEX", min_value=1, max_value=30, value=10)
                    val_con = s3.number_input("CON", min_value=1, max_value=30, value=10)
                    val_int = s4.number_input("INT", min_value=1, max_value=30, value=10)
                    val_wis = s5.number_input("WIS", min_value=1, max_value=30, value=10)
                    val_cha = s6.number_input("CHA", min_value=1, max_value=30, value=10)
                    stats_json = json.dumps({
                        "STR": int(val_str), "DEX": int(val_dex), "CON": int(val_con),
                        "INT": int(val_int), "WIS": int(val_wis), "CHA": int(val_cha)
                    })

                spells_and_features = st.text_area("Büyüler & Özel Yetenekler (İsteğe bağlı)", height=100)

        elif entityType == "item":
            itemType = st.text_input("Tür")
            rarity = st.text_input("Nadirlik")
            value = st.text_input("Değer")
            specialS = st.text_input("Özel yetenek")

            all_chars = [e for e in WorldManager.get_all_entities() if e.entity_type == "character"]
            selected_owner = st.selectbox(
                "Sahibi (Karakter - İsteğe bağlı)",
                options=[None] + all_chars,
                format_func=lambda x:"Sahipsiz" if x is None else x.name
            )
            all_places = [e for e in WorldManager.get_all_entities() if e.entity_type in ["location","district"]]
            selected_place = st.selectbox(
                "Bulunduğu Yer / Dükkan (İsteğe Bağlı)",
                options=[None] + all_places,
                format_func=lambda x:"- Bilinmiyor / Belirtilmemiş - " if x is None else x.name
            )

        elif entityType == "location":
            population = st.text_input("Nüfus")
            religion = st.text_input("Din")
            climate = st.text_input("İklim")
            ruler = st.text_input("Yönetici")

        elif entityType == "god":
            alignment = st.text_input("Yönelim (Alignment)")
            domain = st.text_input("Etki Alanı (Domain - Örn: Savaş, Işık)")
            symbol = st.text_input("Kutsal Sembol")

        elif entityType == "district":
            all_locs = [e for e in WorldManager.get_all_entities() if e.entity_type == "location"]
            if not all_locs:
                st.warning("⚠️ Henüz hiç şehir oluşturmadınız! Önce bir şehir oluşturmalısınız.")
                selected_loc = None
            else:
                selected_loc = st.selectbox("Hangi Şehre/Bölgeye Bağlı? *", options=all_locs, format_func=lambda x: x.name)
            district_type = st.text_input("Mekan Türü (Örn: Bar/Taverna, Ticaret Meydanı)")
            ruler_or_owner = st.text_input("Sahibi / İşletmecisi")

        elif entityType == "faction":
            faction_type = st.text_input("Lonca Türü (Örn: Hırsızlar Loncası,Büyü Akademisi)")
            leader = st.text_input("Lideri / Üstadı")
            headquarters = st.text_input("Merkez Karagahı ")
            motto = st.text_input("Motto / Slogan")
            alignment = st.text_input("Yönelim")

        elif entityType == "monster":
            c_m1, c_m2, c_m3 = st.columns(3)
            m_cr = c_m1.text_input("Zorluk Derecesi (CR)", value="1")
            m_type = c_m2.text_input("Canavar Türü", value="Canavar")
            m_size = c_m3.selectbox("Boyut", ["Minik", "Küçük", "Orta", "Büyük", "Devasa", "Muazzam"], index=2)

            c_m4, c_m5, c_m6 = st.columns(3)
            m_ac = c_m4.number_input("Zırh Sınıfı (AC)", value=12, min_value=1)
            m_hp = c_m5.number_input("Maksimum Can (HP)", value=20, min_value=1)
            m_speed = c_m6.text_input("Hız", value="30 ft")

            st.markdown("###### Temel Statlar:")
            s1, s2, s3, s4, s5, s6 = st.columns(6)
            mv_str = s1.number_input("STR", value=10, min_value=1, max_value=30)
            mv_dex = s2.number_input("DEX", value=10, min_value=1, max_value=30)
            mv_con = s3.number_input("CON", value=10, min_value=1, max_value=30)
            mv_int = s4.number_input("INT", value=10, min_value=1, max_value=30)
            mv_wis = s5.number_input("WIS", value=10, min_value=1, max_value=30)
            mv_cha = s6.number_input("CHA", value=10, min_value=1, max_value=30)

            m_atk_name = st.text_input("Temel Saldırı Adı", value="Pençe / Isırık")
            m_atk_bonus = st.text_input("Saldırı Bonusu", value="+4")
            m_atk_dmg = st.text_input("Hasar Zarı", value="1d8+2 Kesici")
            m_traits = st.text_area("Özel Nitelikler & Pasif Yetenekler", placeholder="Karanlık Görüşü 60 ft, vb.")

        content = st.text_area("İçerik", height=200)

        uploaded_image = st.file_uploader(
            "Fotoğraf / Portre Ekle (İsteğe bağlı)", 
            type=["png", "jpg", "jpeg", "webp"]
        )

        submitted = st.form_submit_button("Oluştur")

    if not submitted:
        return

    name = name.strip()
    if not name:
        st.error("İsim boş olamaz.")
        return
    if WorldManager.getEntityByName(name):
        st.error(f"'{name}' adında bir sayfa zaten var.")
        return

    image_path = saveUploadedImage(uploaded_image)

    if entityType == "character":
        f_id = selected_faction.id if selected_faction else None
        new = WorldManager.create_character(
            name, race, charClass, alignment, faction_id=f_id, faction_role=faction_role,
            is_player=is_player, player_name=player_name, level=level,
            hp_current=hp_current, hp_max=hp_max, armor_class=armor_class, speed=speed,
            stats_json=stats_json, spells_and_features=spells_and_features,
            aliases=aliases, image_path=image_path
        )
    elif entityType == "item":
        o_id = selected_owner.id if selected_owner else None
        l_id = selected_place.id if selected_place else None
        new = WorldManager.create_item(
            name, itemType, rarity, value, specialS, owner_id=o_id, location_id=l_id, aliases=aliases, image_path=image_path
        )
    elif entityType == "location":
        new = WorldManager.create_location(
            name, population, religion, climate, ruler, aliases=aliases, image_path=image_path
        )
    elif entityType == "god":
        new = WorldManager.create_god(
            name, alignment, domain, symbol=symbol, aliases=aliases, image_path=image_path
        )
    elif entityType == "district":
        if not selected_loc:
            st.error("Bir şehre bağlamadan mekan oluşturamazsınız.")
            return
        new = WorldManager.create_district(
            name, selected_loc.id, district_type, ruler_or_owner=ruler_or_owner, aliases=aliases, image_path=image_path
        )
    elif entityType == "faction":
        new = WorldManager.create_faction(
            name, faction_type, leader=leader, headquarters=headquarters, motto=motto, alignment=alignment, aliases=aliases, image_path=image_path
        )
    elif entityType == "monster":
        m_stats_j = json.dumps({
            "STR": int(mv_str), "DEX": int(mv_dex), "CON": int(mv_con),
            "INT": int(mv_int), "WIS": int(mv_wis), "CHA": int(mv_cha)
        })
        m_actions_j = json.dumps([{
            "name": m_atk_name, "bonus": m_atk_bonus, "damage": m_atk_dmg, "desc": "Temel saldırı."
        }])
        new = WorldManager.create_monster(
            name, cr=m_cr, monster_type=m_type, size=m_size,
            armor_class=int(m_ac), hp_max=int(m_hp), speed=m_speed,
            stats_json=m_stats_j, actions_json=m_actions_j, traits=m_traits,
            aliases=aliases, image_path=image_path
        )

    if new:
        BacklinkManager.saveContent(new.id, content)
        goTo(name)
        st.rerun()
