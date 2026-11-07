import os
import json
import random
import uuid
import streamlit as st
from worldManager import WorldManager
from utils.constants import goTo
from utils.monsters_srd import get_srd_monsters
from utils.dice import get_modifier, roll_d20, roll_dice


def _init_encounter_state():
    """Karşılaşma oturumunu başlatır veya mevcut olanı döner."""
    if "active_encounter" not in st.session_state:
        st.session_state["active_encounter"] = {
            "is_active": False,
            "round": 1,
            "turn_idx": 0,
            "combatants": []
        }
    return st.session_state["active_encounter"]


def render_dm_screen():
    """DM Masası: Canlı Karşılaşma Takipçisi ve Canavar Ansiklopedisi (Bestiary)."""
    st.title("⚔️ DM Masası — Karşılaşma & Canavar Yönetimi")
    st.caption("Oyun anında inisiyatif sırasını yönetin, canavarları sahneye sürün ve anlık can takibi yapın.")

    tab_encounter, tab_bestiary = st.tabs([
        "⚔️ Canlı Karşılaşma (Encounter Runner)",
        "🐉 Canavar Kütüphanesi (Bestiary)"
    ])

    # =========================================================================
    # SEKME 1: CANLI KARŞILAŞMA TAKİPÇİSİ (ENCOUNTER RUNNER)
    # =========================================================================
    with tab_encounter:
        encounter = _init_encounter_state()
        combatants = encounter["combatants"]

        # --- Üst Kontrol Çubuğu ---
        top_c1, top_c2, top_c3, top_c4 = st.columns([1.5, 2, 2, 2], vertical_alignment="center")

        top_c1.markdown(f"### 🛡️ Tur: **{encounter['round']}**")

        if top_c2.button("▶️ Sıradaki Tur (Next Turn)", type="primary", use_container_width=True, disabled=len(combatants) == 0):
            if combatants:
                encounter["turn_idx"] = (encounter["turn_idx"] + 1) % len(combatants)
                if encounter["turn_idx"] == 0:
                    encounter["round"] += 1
                st.rerun()

        if top_c3.button("🔄 İnisiyatife Göre Diz", use_container_width=True, disabled=len(combatants) == 0):
            combatants.sort(key=lambda x: x["init"], reverse=True)
            encounter["turn_idx"] = 0
            st.rerun()

        if top_c4.button("🏁 Karşılaşmayı Bitir", use_container_width=True, disabled=len(combatants) == 0):
            encounter["is_active"] = False
            encounter["round"] = 1
            encounter["turn_idx"] = 0
            encounter["combatants"] = []
            st.session_state.pop("dm_roll_result", None)
            st.success("Karşılaşma sonlandırıldı ve sahne temizlendi.")
            st.rerun()

        # Son Zar Bildirimi
        last_roll = st.session_state.get("dm_roll_result")
        if last_roll:
            st.info(last_roll)

        st.divider()

        # --- Sahneye Savaşçı Ekleme Paneli ---
        with st.expander("➕ Sahneye Savaşçı Ekle (Oyuncu veya Canavar)", expanded=(len(combatants) == 0)):
            col_add_pc, col_add_mob = st.columns(2)

            # Oyuncu Ekleme
            with col_add_pc:
                st.markdown("##### ⭐ Oyuncu Karakteri Ekle")
                all_pcs = WorldManager.get_characters_by_player_status(is_player=True)
                # Zaten sahnede olmayanlar
                active_ids = {c["source_id"] for c in combatants if c.get("source_id")}
                available_pcs = [p for p in all_pcs if p.id not in active_ids]

                if available_pcs:
                    sel_pc = st.selectbox("Oyuncu Seç:", options=available_pcs, format_func=lambda x: f"{x.name} (AC: {getattr(x.character, 'armor_class', 10)})", key="sel_enc_pc")
                    add_pc_init = st.number_input("Manuel İnisiyatif (Masada atılan zar):", value=10, min_value=1, max_value=40, key="inp_pc_init")
                    if st.button("➕ Oyuncuyu Sahneye Ekle", key="btn_add_pc_to_enc", use_container_width=True):
                        c_stat = sel_pc.character
                        hp_m = getattr(c_stat, "hp_max", 10) or 10
                        hp_c = getattr(c_stat, "hp_current", hp_m)
                        if hp_c is None:
                            hp_c = hp_m
                        combatants.append({
                            "id": str(uuid.uuid4())[:8],
                            "source_id": sel_pc.id,
                            "name": sel_pc.name,
                            "type": "pc",
                            "init": int(add_pc_init),
                            "ac": getattr(c_stat, "armor_class", 10) or 10,
                            "hp_cur": hp_c,
                            "hp_max": hp_m,
                            "speed": getattr(c_stat, "speed", "30 ft") or "30 ft",
                            "stats": getattr(c_stat, "stats_json", ""),
                            "actions": [],
                            "traits": getattr(c_stat, "spells_and_features", "")
                        })
                        encounter["is_active"] = True
                        st.rerun()
                else:
                    st.caption("Eklenebilecek uygun oyuncu bulunamadı.")

            # Canavar Ekleme
            with col_add_mob:
                st.markdown("##### 🐉 Canavar Sürüsü Ekle")
                all_mobs = WorldManager.get_all_monsters()
                if all_mobs:
                    sel_mob = st.selectbox("Canavar Seç:", options=all_mobs, format_func=lambda x: f"{x.name} (CR: {getattr(x.monster, 'cr', '1')})", key="sel_enc_mob")
                    count_col, init_col = st.columns(2)
                    mob_count = count_col.number_input("Adet:", min_value=1, max_value=10, value=1, key="inp_mob_count")
                    auto_init = init_col.checkbox("🎲 Otomatik İnisiyatif At", value=True, key="chk_mob_auto_init")

                    if st.button("🚀 Canavarları Sahneye Sür", key="btn_add_mob_to_enc", type="primary", use_container_width=True):
                        m_stat = sel_mob.monster
                        dex_mod = 0
                        try:
                            m_stats = json.loads(getattr(m_stat, "stats_json", "") or "{}")
                            dex_mod = get_modifier(int(m_stats.get("DEX", 10)))
                        except Exception:
                            dex_mod = 0

                        for i in range(int(mob_count)):
                            m_init = (random.randint(1, 20) + dex_mod) if auto_init else 10
                            c_name = f"{sel_mob.name} #{i+1}" if mob_count > 1 else sel_mob.name
                            hp_m = getattr(m_stat, "hp_max", 10) or 10

                            raw_actions = getattr(m_stat, "actions_json", "") or "[]"
                            try:
                                actions_list = json.loads(raw_actions) if raw_actions else []
                            except Exception:
                                actions_list = []

                            combatants.append({
                                "id": str(uuid.uuid4())[:8],
                                "source_id": sel_mob.id,
                                "name": c_name,
                                "type": "monster",
                                "init": m_init,
                                "ac": getattr(m_stat, "armor_class", 10) or 10,
                                "hp_cur": hp_m,
                                "hp_max": hp_m,
                                "speed": getattr(m_stat, "speed", "30 ft") or "30 ft",
                                "stats": getattr(m_stat, "stats_json", ""),
                                "actions": actions_list,
                                "traits": getattr(m_stat, "traits", "")
                            })
                        encounter["is_active"] = True
                        st.rerun()
                else:
                    st.caption("Kayıtlı canavar yok. Yan sekmeden hazır canavarları yükleyebilir veya yenisini oluşturabilirsiniz.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Aktif Savaşçılar Listesi (Turn Tracker) ---
        if not combatants:
            st.info("Sahne şu an boş. Yukarıdaki panelden oyuncuları ve canavarları ekleyerek savaşı başlatın!")
        else:
            current_idx = encounter["turn_idx"] % len(combatants)

            for idx, c in enumerate(combatants):
                is_turn = (idx == current_idx)
                border_color = "#3b82f6" if is_turn else "#e5e7eb"
                is_dead = (c["hp_cur"] <= 0)

                with st.container(border=True):
                    row1, row2, row3, row4, row5 = st.columns([0.8, 3, 2, 3, 1], vertical_alignment="center")

                    # Sıra Göstergesi
                    with row1:
                        if is_turn:
                            st.markdown("### 👉")
                        else:
                            st.markdown(f"**#{idx+1}**")

                    # İsim ve Tür
                    with row2:
                        type_badge = "⭐ OYUNCU" if c["type"] == "pc" else "🐉 CANAVAR"
                        dead_text = " ~ 💀 **ÖLDÜ / BAYGIN**" if is_dead else ""
                        st.markdown(f"**{c['name']}** <small>({type_badge})</small>{dead_text}", unsafe_allow_html=True)
                        st.caption(f"🛡️ AC: **{c['ac']}** | 🏃 Hız: **{c['speed']}**")

                    # İnisiyatif (Kullanıcının talep ettiği gibi DÜZENLENEBİLİR)
                    with row3:
                        new_init = st.number_input(
                            "İnisiyatif",
                            value=int(c["init"]),
                            key=f"init_val_{c['id']}",
                            label_visibility="collapsed",
                            min_value=-5, max_value=50
                        )
                        if new_init != c["init"]:
                            c["init"] = int(new_init)

                    # Can (HP) ve Hasar Butonları
                    with row4:
                        hp_ratio = max(0.0, min(1.0, c["hp_cur"] / max(1, c["hp_max"])))
                        st.progress(hp_ratio, text=f"❤️ {c['hp_cur']} / {c['hp_max']} HP")

                        b1, b2, b3, b4 = st.columns(4)
                        if b1.button("-5", key=f"dmg5_{c['id']}", disabled=is_dead):
                            c["hp_cur"] = max(0, c["hp_cur"] - 5)
                            st.rerun()
                        if b2.button("-1", key=f"dmg1_{c['id']}", disabled=is_dead):
                            c["hp_cur"] = max(0, c["hp_cur"] - 1)
                            st.rerun()
                        if b3.button("+1", key=f"heal1_{c['id']}"):
                            c["hp_cur"] = min(c["hp_max"], c["hp_cur"] + 1)
                            st.rerun()
                        if b4.button("+5", key=f"heal5_{c['id']}"):
                            c["hp_cur"] = min(c["hp_max"], c["hp_cur"] + 5)
                            st.rerun()

                    # Çıkar Butonu
                    with row5:
                        if st.button("❌", key=f"del_c_{c['id']}", help="Sahneden Çıkar"):
                            combatants.pop(idx)
                            if encounter["turn_idx"] >= len(combatants) and len(combatants) > 0:
                                encounter["turn_idx"] = 0
                            st.rerun()

                    # Canavar Saldırıları & Zarları (Genişletilebilir Alan)
                    if c.get("actions"):
                        with st.expander(f"⚔️ {c['name']} Saldırıları & Yetenekleri"):
                            act_cols = st.columns(min(len(c["actions"]), 3))
                            for a_idx, act in enumerate(c["actions"]):
                                with act_cols[a_idx % len(act_cols)]:
                                    st.markdown(f"**{act.get('name')}**")
                                    st.caption(f"💥 Hasar: {act.get('damage', '-')}")
                                    bonus_str = act.get('bonus', '+0')
                                    if st.button(f"🎲 Zar At ({bonus_str})", key=f"roll_act_{c['id']}_{a_idx}"):
                                        try:
                                            b_val = int(bonus_str.replace("+", "").strip())
                                        except Exception:
                                            b_val = 0
                                        d20, total = roll_d20(bonus=b_val)
                                        crit = " — 💥 KRİTİK BAŞARI!" if d20 == 20 else (" — 💀 KRİTİK ISKALAMA!" if d20 == 1 else "")
                                        dmg_expr = act.get('damage', '-')
                                        dmg_rolled, dmg_breakdown = roll_dice(dmg_expr)
                                        if dmg_rolled > 0:
                                            st.session_state["dm_roll_result"] = f"🎲 **{c['name']} ➔ {act.get('name')}:** Saldırı d20 ({d20}) {bonus_str} = **{total}** {crit} | 💥 Hasar: **{dmg_rolled}** ({dmg_breakdown})"
                                        else:
                                            st.session_state["dm_roll_result"] = f"🎲 **{c['name']} ➔ {act.get('name')}:** Saldırı d20 ({d20}) {bonus_str} = **{total}** {crit}"
                                        st.rerun()

    # =========================================================================
    # SEKME 2: CANAVAR ANSİKLOPEDİSİ (BESTIARY)
    # =========================================================================
    with tab_bestiary:
        st.subheader("🐉 Canavar Kütüphanesi & Şablonlar")

        # Üst Araçlar: Yeni Canavar Oluştur veya Hazır Canavarları Yükle
        b_c1, b_c2 = st.columns([1, 1])

        with b_c1:
            with st.expander("✨ Yeni Canavar Yarat (Sıfırdan Ekle)"):
                with st.form("form_create_monster_dm"):
                    m_name = st.text_input("Canavar Adı *", placeholder="Örn: Gölge Ejderhası")
                    mc_1, mc_2, mc_3 = st.columns(3)
                    m_cr = mc_1.text_input("CR (Zorluk)", value="1")
                    m_type = mc_2.text_input("Türü", value="Canavar")
                    m_size = mc_3.selectbox("Boyutu", ["Minik", "Küçük", "Orta", "Büyük", "Devasa", "Muazzam"], index=2)

                    mc_4, mc_5, mc_6 = st.columns(3)
                    m_ac = mc_4.number_input("Zırh Sınıfı (AC)", value=12, min_value=1)
                    m_hp = mc_5.number_input("Can Puanı (HP)", value=20, min_value=1)
                    m_speed = mc_6.text_input("Hız", value="30 ft")

                    st.markdown("###### Temel Statlar:")
                    s1, s2, s3, s4, s5, s6 = st.columns(6)
                    v_str = s1.number_input("STR", value=10, min_value=1, max_value=30)
                    v_dex = s2.number_input("DEX", value=10, min_value=1, max_value=30)
                    v_con = s3.number_input("CON", value=10, min_value=1, max_value=30)
                    v_int = s4.number_input("INT", value=10, min_value=1, max_value=30)
                    v_wis = s5.number_input("WIS", value=10, min_value=1, max_value=30)
                    v_cha = s6.number_input("CHA", value=10, min_value=1, max_value=30)

                    m_attack_name = st.text_input("Temel Saldırı Adı", value="Pençe")
                    m_attack_bonus = st.text_input("Saldırı Bonusu", value="+4")
                    m_attack_dmg = st.text_input("Hasar Zarı", value="1d8+2 Kesici")
                    m_traits = st.text_area("Özel Nitelikler & Pasifler (İsteğe bağlı)", placeholder="Karanlık Görüşü, Büyü Direnci...")

                    submit_mob = st.form_submit_button("💾 Canavarı Kaydet", type="primary", use_container_width=True)

                    if submit_mob:
                        m_name = m_name.strip()
                        if not m_name:
                            st.error("Lütfen bir canavar adı girin.")
                        elif WorldManager.getEntityByName(m_name):
                            st.error(f"'{m_name}' adında bir kayıt zaten var.")
                        else:
                            stats_j = json.dumps({
                                "STR": int(v_str), "DEX": int(v_dex), "CON": int(v_con),
                                "INT": int(v_int), "WIS": int(v_wis), "CHA": int(v_cha)
                            })
                            actions_j = json.dumps([{
                                "name": m_attack_name,
                                "bonus": m_attack_bonus,
                                "damage": m_attack_dmg,
                                "desc": "Temel saldırı."
                            }])
                            new_mob = WorldManager.create_monster(
                                name=m_name, cr=m_cr, monster_type=m_type, size=m_size,
                                armor_class=int(m_ac), hp_max=int(m_hp), speed=m_speed,
                                stats_json=stats_j, actions_json=actions_j, traits=m_traits
                            )
                            st.success(f"{m_name} başarıyla Bestiary'ye eklendi!")
                            st.rerun()

        with b_c2:
            with st.expander("📦 Klasik SRD Canavarlarını Yükle"):
                st.caption("D&D 5e'nin en çok kullanılan 9 klasik canavarını (Goblin, Kurt, İskelet, Zombi, Ogre, Haydut, Ejderha vb.) tek tıkla bu evrene aktarabilirsiniz.")
                if st.button("🚀 Hazır Canavarları Bu Evrene İçe Aktar", key="btn_import_srd", use_container_width=True):
                    srd_list = get_srd_monsters()
                    added_count = 0
                    for m_data in srd_list:
                        res = WorldManager.import_srd_monster(m_data)
                        if res:
                            added_count += 1
                    st.success(f"Canavarlar kontrol edildi / eklendi! ({len(srd_list)} şablon hazır)")
                    st.rerun()

        st.divider()

        # Kayıtlı Canavarlar Listesi
        monsters = WorldManager.get_all_monsters()
        if not monsters:
            st.info("Bu evrende henüz kayıtlı canavar yok. Yukarıdaki panelden yeni bir canavar yaratabilir veya hazır SRD canavarlarını tek tıkla yükleyebilirsiniz.")
        else:
            search_mob = st.text_input("🔍 Canavar Ara:", placeholder="Goblin, Kurt, Ejderha...", key="search_bestiary")
            if search_mob:
                monsters = [m for m in monsters if search_mob.lower() in m.name.lower()]

            st.caption(f"Kütüphanede **{len(monsters)}** canavar bulundu:")

            for mob in sorted(monsters, key=lambda x: x.name):
                m_info = mob.monster
                cr_str = getattr(m_info, 'cr', '1') or '1'
                ac_val = getattr(m_info, 'armor_class', 10) or 10
                hp_val = getattr(m_info, 'hp_max', 10) or 10
                spd_val = getattr(m_info, 'speed', '30 ft') or '30 ft'

                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2], vertical_alignment="center")

                    with c1:
                        st.markdown(f"### 🐉 {mob.name}")
                        st.caption(f"**CR {cr_str}** — {getattr(m_info, 'size', 'Orta')} {getattr(m_info, 'monster_type', 'Canavar')}")

                    with c2:
                        st.write(f"🛡️ AC: **{ac_val}** | ❤️ HP: **{hp_val}**")
                        st.caption(f"🏃 Hız: {spd_val}")

                    with c3:
                        if st.button("⚔️ Sahneye Sür", key=f"quick_stage_{mob.id}", use_container_width=True, type="primary"):
                            encounter = _init_encounter_state()
                            raw_acts = getattr(m_info, "actions_json", "") or "[]"
                            try:
                                a_list = json.loads(raw_acts) if raw_acts else []
                            except Exception:
                                a_list = []

                            dex_mod = 0
                            try:
                                s_dict = json.loads(getattr(m_info, "stats_json", "") or "{}")
                                dex_mod = (int(s_dict.get("DEX", 10)) - 10) // 2
                            except Exception:
                                dex_mod = 0

                            encounter["combatants"].append({
                                "id": str(uuid.uuid4())[:8],
                                "source_id": mob.id,
                                "name": mob.name,
                                "type": "monster",
                                "init": random.randint(1, 20) + dex_mod,
                                "ac": ac_val,
                                "hp_cur": hp_val,
                                "hp_max": hp_val,
                                "speed": spd_val,
                                "stats": getattr(m_info, "stats_json", ""),
                                "actions": a_list,
                                "traits": getattr(m_info, "traits", "")
                            })
                            encounter["is_active"] = True
                            st.success(f"{mob.name} sahneye sürüldü! (İnisiyatif zarı atıldı)")
                            st.rerun()

                    with c4:
                        st.button("📖 Sayfasını Aç", key=f"open_mob_{mob.id}", on_click=goTo, args=(mob.name,), use_container_width=True)
