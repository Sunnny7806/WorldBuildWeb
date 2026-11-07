import json
import random
import streamlit as st
from worldManager import WorldManager
from utils.constants import goTo
from utils.dice import get_modifier, format_modifier, roll_d20

def render_character_sheet(entity):
    """Karakter Kâğıdı (Stat Block), Canlı Can Barı ve Envanter sekmelerini render eder."""
    c = entity.character
    if not c:
        return

    st.divider()
    tab_sheet, tab_inv = st.tabs(["📊 Karakter Kâğıdı (Stat Block)", "🎒 Envanter (Çanta)"])

    with tab_sheet:
        # 1. Özet Metrikler
        m1, m2, m3, m4 = st.columns(4)
        type_label = "⭐ Oyuncu (PC)" if getattr(c, 'is_player', False) else "🎭 NPC"
        if getattr(c, 'is_player', False) and getattr(c, 'player_name', ''):
            type_label += f" ({c.player_name})"
        m1.metric("Karakter Türü", type_label)
        m2.metric("Seviye (Level)", getattr(c, 'level', 1) or 1)
        m3.metric("Zırh Sınıfı (AC)", getattr(c, 'armor_class', 10) or 10)
        m4.metric("Hız (Speed)", getattr(c, 'speed', '30 ft') or '30 ft')

        # 2. Can (HP) Barı & Hızlı Butonlar
        hp_max = getattr(c, 'hp_max', 10) or 10
        hp_cur = getattr(c, 'hp_current', hp_max)
        if hp_cur is None:
            hp_cur = hp_max
        hp_ratio = max(0.0, min(1.0, hp_cur / max(1, hp_max)))
        st.progress(hp_ratio, text=f"❤️ Can Puanı: {hp_cur} / {hp_max} HP")

        hpc1, hpc2, hpc3, hpc4, hpc5 = st.columns([1, 1, 1, 1, 2], vertical_alignment="center")
        if hpc1.button("💥 -5 Can", key=f"hp_m5_{entity.id}", use_container_width=True):
            WorldManager.update_character_hp(entity.id, -5)
            st.rerun()
        if hpc2.button("🩸 -1 Can", key=f"hp_m1_{entity.id}", use_container_width=True):
            WorldManager.update_character_hp(entity.id, -1)
            st.rerun()
        if hpc3.button("🧪 +1 Can", key=f"hp_p1_{entity.id}", use_container_width=True):
            WorldManager.update_character_hp(entity.id, +1)
            st.rerun()
        if hpc4.button("✨ +5 Can", key=f"hp_p5_{entity.id}", use_container_width=True):
            WorldManager.update_character_hp(entity.id, +5)
            st.rerun()
        if hpc5.button("💚 Tam İyileş", key=f"hp_full_{entity.id}", use_container_width=True):
            WorldManager.update_character_hp(entity.id, hp_max)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Son Zar Sonucu Bildirimi
        last_roll_key = f"last_roll_{entity.id}"
        last_roll = st.session_state.get(last_roll_key)
        if last_roll:
            st.info(last_roll)

        # 3. 6 Yetenek Skoru & Zar Butonları
        st.markdown("##### 🎲 Yetenek Skorları & Kontrol Zarları")
        default_stats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        raw_stats = getattr(c, 'stats_json', '') or ''
        try:
            stats_dict = json.loads(raw_stats) if raw_stats else default_stats
        except Exception:
            stats_dict = default_stats

        stat_cols = st.columns(6)
        stat_labels = [
            ("STR", "Kuvvet"), ("DEX", "Çeviklik"), ("CON", "Dayanıklılık"),
            ("INT", "Zekâ"), ("WIS", "Bilgelik"), ("CHA", "Karizma")
        ]

        for idx, (abbr, full_name) in enumerate(stat_labels):
            score = int(stats_dict.get(abbr, 10))
            mod_val = get_modifier(score)
            mod_str = format_modifier(score)

            with stat_cols[idx]:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='text-align:center;'><b>{abbr}</b><br><small>{full_name}</small><br>"
                        f"<h2 style='margin:2px 0;'>{score}</h2></div>", 
                        unsafe_allow_html=True
                    )
                    if st.button(f"🎲 {mod_str}", key=f"roll_{abbr}_{entity.id}", use_container_width=True):
                        d20, total = roll_d20(bonus=mod_val)
                        crit = " — 💥 KRİTİK BAŞARI (20)!" if d20 == 20 else (" — 💀 KRİTİK BAŞARISIZLIK (1)!" if d20 == 1 else "")
                        st.session_state[last_roll_key] = f"🎲 **{full_name} ({abbr}) Kontrolü:** d20 (**{d20}**) {mod_str} = **{total}**{crit}"
                        st.rerun()

        # 4. Büyüler ve Özel Yetenekler
        spells_content = getattr(c, 'spells_and_features', '')
        if spells_content:
            st.markdown("---")
            st.markdown("##### ✨ Büyüler & Özel Yetenekler")
            st.markdown(spells_content)

        # 5. Hızlı Düzenleme Paneli
        with st.expander("⚙️ Karakter Kâğıdını Düzenle (Statlar, Seviye, AC, Büyüler)"):
            ed_c1, ed_c2 = st.columns(2)
            ed_is_player = ed_c1.checkbox("⭐ Oyuncu Karakteri (PC)", value=getattr(c, 'is_player', False), key=f"ed_pc_{entity.id}")
            ed_player_name = ed_c2.text_input("Oyuncu Adı", value=getattr(c, 'player_name', '') or '', key=f"ed_pname_{entity.id}")

            ed_c3, ed_c4, ed_c5, ed_c6 = st.columns(4)
            ed_level = ed_c3.number_input("Seviye", min_value=1, max_value=20, value=getattr(c, 'level', 1) or 1, key=f"ed_lvl_{entity.id}")
            ed_hp_max = ed_c4.number_input("Max HP", min_value=1, value=hp_max, key=f"ed_hpmax_{entity.id}")
            ed_ac = ed_c5.number_input("AC", min_value=1, value=getattr(c, 'armor_class', 10) or 10, key=f"ed_ac_{entity.id}")
            ed_speed = ed_c6.text_input("Hız", value=getattr(c, 'speed', '30 ft') or '30 ft', key=f"ed_spd_{entity.id}")

            st.markdown("###### Yetenek Skorları:")
            es1, es2, es3, es4, es5, es6 = st.columns(6)
            n_str = es1.number_input("STR", min_value=1, max_value=30, value=int(stats_dict.get("STR", 10)), key=f"ed_str_{entity.id}")
            n_dex = es2.number_input("DEX", min_value=1, max_value=30, value=int(stats_dict.get("DEX", 10)), key=f"ed_dex_{entity.id}")
            n_con = es3.number_input("CON", min_value=1, max_value=30, value=int(stats_dict.get("CON", 10)), key=f"ed_con_{entity.id}")
            n_int = es4.number_input("INT", min_value=1, max_value=30, value=int(stats_dict.get("INT", 10)), key=f"ed_int_{entity.id}")
            n_wis = es5.number_input("WIS", min_value=1, max_value=30, value=int(stats_dict.get("WIS", 10)), key=f"ed_wis_{entity.id}")
            n_cha = es6.number_input("CHA", min_value=1, max_value=30, value=int(stats_dict.get("CHA", 10)), key=f"ed_cha_{entity.id}")

            ed_spells = st.text_area("Büyüler & Özel Yetenekler", value=spells_content or '', height=100, key=f"ed_spells_{entity.id}")

            if st.button("💾 Karakter Kâğıdını Kaydet", key=f"btn_save_sheet_{entity.id}", type="primary", use_container_width=True):
                new_stats_json = json.dumps({
                    "STR": int(n_str), "DEX": int(n_dex), "CON": int(n_con),
                    "INT": int(n_int), "WIS": int(n_wis), "CHA": int(n_cha)
                })
                WorldManager.updateEntity(
                    entity.id,
                    is_player=ed_is_player,
                    player_name=ed_player_name,
                    level=int(ed_level),
                    hp_max=int(ed_hp_max),
                    armor_class=int(ed_ac),
                    speed=ed_speed,
                    stats_json=new_stats_json,
                    spells_and_features=ed_spells
                )
                st.success("Karakter kâğıdı başarıyla güncellendi!")
                st.rerun()

    with tab_inv:
        st.subheader("🎒 Envanter (Taşıdığı Eşyalar)")
        inventory = WorldManager.get_character_inventory(entity.id)
        if inventory:
            for item in inventory:
                st.button(f"💎 {item.name}", key=f"inv_{item.id}", on_click=goTo, args=(item.name,))
        else:
            st.caption("Bu karakterin üzerinde kayıtlı bir eşya yok.")

        # Karakterin Çantasına Hızlı Eşya Koyma
        with st.expander("➕ Çantaya Eşya Ekle / Devret"):
            all_items = [e for e in WorldManager.get_all_entities() if e.entity_type == "item"]
            available_items = [it for it in all_items if not it.item or it.item.owner_id != entity.id]
            if available_items:
                c_it1, c_it2 = st.columns([3, 1], vertical_alignment="bottom")
                chosen_item = c_it1.selectbox(
                    "Eşya Seç:", 
                    options=available_items, 
                    format_func=lambda x: x.name, 
                    key=f"give_item_{entity.id}"
                )
                if c_it2.button("🎒 Çantaya Ver", key=f"btn_give_{entity.id}", use_container_width=True):
                    WorldManager.updateEntity(chosen_item.id, owner_id=entity.id, location_id=None)
                    st.success(f"{chosen_item.name} çantaya eklendi!")
                    st.rerun()
            else:
                st.caption("Verilebilecek başka eşya bulunmuyor.")
