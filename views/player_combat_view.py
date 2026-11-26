import streamlit as st
from worldManager import WorldManager


def render_player_combat_view():
    """Oyuncular için salt-okunur canlı savaş sırası (Canavar statları ve canı blurlu/sansürlü)."""
    top_l, top_r = st.columns([4, 1], vertical_alignment="center")
    top_l.title("⚔️ Canlı Savaş Panosu (İnisiyatif)")
    if top_r.button("🔄 Durumu Yenile", use_container_width=True):
        st.rerun()

    st.caption("Tur sırasını buradan takip edebilirsiniz.")

    encounter = WorldManager.get_encounter()
    combatants = encounter.get("combatants", [])

    if not encounter.get("is_active") or not combatants:
        st.info("Şu an aktif bir savaş bulunmuyor.")
        return

    st.markdown(f"### 🛡️ Tur: **{encounter.get('round', 1)}**")
    st.divider()

    current_idx = encounter.get("turn_idx", 0) % len(combatants)

    for idx, c in enumerate(combatants):
        is_turn = (idx == current_idx)
        is_dead = (c.get("hp_cur", 0) <= 0)
        is_monster = (c.get("type") == "monster")

        with st.container(border=True):
            col_turn, col_info, col_hp = st.columns([0.8, 3.2, 3], vertical_alignment="center")

            with col_turn:
                if is_turn:
                    st.markdown("### 👉")
                else:
                    st.markdown(f"**#{idx + 1}**")

            with col_info:
                type_badge = "🐉 DÜŞMAN" if is_monster else "⭐ OYUNCU"
                dead_text = " ~ 💀 **SAF DIŞI**" if is_dead else ""
                st.markdown(f"**{c['name']}** — 🎲 İnisiyatif: **{c['init']}** <small>({type_badge})</small>{dead_text}", unsafe_allow_html=True)

                if is_monster:
                    # Gerçek AC/Hız değerleri HTML içine dahi yazılmaz; F12 ile incelense bile gizli kalır
                    st.markdown(
                        "<span style='filter: blur(5px); user-select: none; opacity: 0.7;'>🛡️ AC: 18 | 🏃 Hız: 30 ft</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.caption(f"🛡️ AC: **{c['ac']}** | 🏃 Hız: **{c['speed']}**")

            with col_hp:
                if is_monster:
                    if is_dead:
                        st.markdown("💀 **Devre Dışı / Öldü**")
                    else:
                        st.markdown(
                            "<div style='filter: blur(5px); user-select: none; padding: 6px 10px; "
                            "border-radius: 6px; background: rgba(220, 38, 38, 0.12); text-align: center;'>"
                            "❤️ 88 / 120 HP — Durum Bilinmiyor</div>",
                            unsafe_allow_html=True
                        )
                else:
                    hp_max = max(1, c.get("hp_max", 10))
                    hp_cur = max(0, c.get("hp_cur", 0))
                    hp_ratio = max(0.0, min(1.0, hp_cur / hp_max))
                    st.progress(hp_ratio, text=f"❤️ {hp_cur} / {hp_max} HP")
