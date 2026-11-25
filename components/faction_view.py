import streamlit as st
from worldManager import WorldManager
from utils.constants import goTo
from utils.generators import generate_roster

def render_faction_view(entity):
    """Lonca (Faction) üyelerini ve rastgele 5 kişilik kadro üretim zarı panelini render eder."""
    if not entity.faction:
        return

    st.divider()
    st.subheader("👥 Lonca Üyeleri & Kadro")
    members = WorldManager.get_faction_members(entity.id)

    if members:
        for m in members:
            mc1, mc2 = st.columns([3, 2], vertical_alignment="center")
            role_text = m.character.faction_role if m.character and m.character.faction_role else "Üye"
            mc1.button(f"🧙 {m.name}", key=f"mem_{m.id}", on_click=goTo, args=(m.name,), use_container_width=True)
            mc2.caption(f"🎖️ {role_text}")
    else:
        st.info("Bu loncaya henüz kayıtlı bir üye yok.")

    # 🎲 HIZLI KADRO ÜRETİCİSİ (ZAR SİSTEMİ)
    with st.expander("🎲 Hızlı Üye Kadrosu Üret (5 Kişi)"):
        st.caption("Loncanın türüne uygun rastgele isim ve rol kombinasyonları üretir. İsimleri dilediğiniz gibi düzenleyip tek tıkla kaydedebilirsiniz.")
        
        roster_key = f"temp_roster_{entity.id}"
        
        if st.button("🎲 Zar At & Yeni Kadro Öner", key=f"roll_{entity.id}"):
            st.session_state[roster_key] = generate_roster(entity.faction.faction_type, count=5)
            st.rerun()

        cur_roster = st.session_state.get(roster_key)
        if cur_roster:
            st.markdown("##### Önerilen Kadro:")
            edited_roster = []
            for idx, person in enumerate(cur_roster):
                rc1, rc2 = st.columns([3, 2])
                p_name = rc1.text_input(f"İsim #{idx+1}", value=person["name"], key=f"r_name_{entity.id}_{idx}")
                p_role = rc2.text_input(f"Rol/Rütbe #{idx+1}", value=person["role"], key=f"r_role_{entity.id}_{idx}")
                edited_roster.append({"name": p_name, "role": p_role})

            btn_c1, btn_c2 = st.columns([3, 1])
            if btn_c1.button("💾 Bu Kadroyu Loncaya Kaydet", key=f"save_roster_{entity.id}", type="primary", use_container_width=True):
                WorldManager.bulk_add_faction_members(entity.id, edited_roster)
                st.session_state.pop(roster_key, None)
                st.success("Kadro başarıyla loncaya eklendi!")
                st.rerun()
            if btn_c2.button("İptal", key=f"cancel_roster_{entity.id}", use_container_width=True):
                st.session_state.pop(roster_key, None)
                st.rerun()
