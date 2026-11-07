import json
import random
import uuid
import streamlit as st
from utils.dice import get_modifier, format_modifier

def render_monster_stat_block(entity):
    """Canavar (Monster) Stat Bloğunu ve DM Encounter'a sahneleme butonunu render eder."""
    m = entity.monster
    if not m:
        return

    st.divider()
    st.subheader("🐉 Canavar Stat Bloğu")

    # 1. Metrikler & Sahneye Sür Butonu
    mb1, mb2, mb3, mb4 = st.columns([1.5, 1.5, 1.5, 2.5], vertical_alignment="center")
    mb1.metric("Zorluk (CR)", f"CR {m.cr or '1'}")
    mb2.metric("Zırh Sınıfı (AC)", m.armor_class or 10)
    mb3.metric("Maks Can (HP)", f"{m.hp_max or 10} HP")

    with mb4:
        if st.button("⚔️ Sahneye Sür (DM Karşılaşmasına Ekle)", type="primary", use_container_width=True, key=f"stage_from_page_{entity.id}"):
            if "active_encounter" not in st.session_state:
                st.session_state["active_encounter"] = {"is_active": True, "round": 1, "turn_idx": 0, "combatants": []}
            enc = st.session_state["active_encounter"]

            dex_mod = 0
            try:
                s_dict = json.loads(m.stats_json or "{}")
                dex_mod = get_modifier(int(s_dict.get("DEX", 10)))
            except Exception:
                dex_mod = 0

            raw_acts = m.actions_json or "[]"
            try:
                act_list = json.loads(raw_acts) if raw_acts else []
            except Exception:
                act_list = []

            enc["combatants"].append({
                "id": str(uuid.uuid4())[:8],
                "source_id": entity.id,
                "name": entity.name,
                "type": "monster",
                "init": random.randint(1, 20) + dex_mod,
                "ac": m.armor_class or 10,
                "hp_cur": m.hp_max or 10,
                "hp_max": m.hp_max or 10,
                "speed": m.speed or "30 ft",
                "stats": m.stats_json,
                "actions": act_list,
                "traits": m.traits
            })
            enc["is_active"] = True
            st.query_params["page"] = "__dm_screen__"
            st.rerun()

    st.caption(f"**Tür & Boyut:** {m.size} {m.monster_type} | 🏃 **Hız:** {m.speed or '30 ft'}")

    # 2. Yetenek Skorları
    st.markdown("##### 🎲 Yetenek Skorları")
    default_mstats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
    try:
        mstats = json.loads(m.stats_json or "{}") if m.stats_json else default_mstats
    except Exception:
        mstats = default_mstats

    m_cols = st.columns(6)
    stat_meta = [
        ("STR", "Kuvvet"), ("DEX", "Çeviklik"), ("CON", "Dayanıklılık"),
        ("INT", "Zekâ"), ("WIS", "Bilgelik"), ("CHA", "Karizma")
    ]
    for idx, (abbr, fname) in enumerate(stat_meta):
        s_val = int(mstats.get(abbr, 10))
        s_mod = format_modifier(s_val)
        with m_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center;'><b>{abbr}</b><br>"
                    f"<h3 style='margin:2px 0;'>{s_val}</h3><small>{s_mod}</small></div>", 
                    unsafe_allow_html=True
                )

    # 3. Saldırılar (Actions)
    raw_acts = m.actions_json or "[]"
    try:
        acts = json.loads(raw_acts) if raw_acts else []
    except Exception:
        acts = []

    if acts:
        st.markdown("##### ⚔️ Eylemler & Saldırılar")
        for a in acts:
            st.markdown(f"**{a.get('name')}**: `{a.get('bonus', '+0')}` vurur, Hasar: **{a.get('damage', '-')}** ({a.get('desc', '')})")

    # 4. Özel Yetenekler (Traits)
    if m.traits:
        st.markdown("##### 📜 Özel Nitelikler & Pasifler")
        st.info(m.traits)
