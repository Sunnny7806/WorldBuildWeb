import streamlit as st
from worldManager import WorldManager
from linker import WikiLinker
from utils.constants import goTo,is_dm_mode,is_visible,renderLinks

def render_session_view():
    dm_mode = is_dm_mode()
    st.title("📖 Oturum Günlüğü (Sessions)")
    st.caption("Oynanan Sessionların Kayıtları")
    sessions = WorldManager.get_session(include_unpublished=dm_mode)
    if dm_mode:
        with st.expander("➕ Yeni Session Ekle"):
            with st.form("form_create_session", clear_on_submit=True):
                c1, c2 = st.columns([1,3])
                ses_num = c1.number_input("Session No",min_value=1,value=WorldManager.get_next_session_number(),step=1)
                ses_title = c2.text_input("Başlık *")
                date = st.text_input("Session'ın Oynandığı Tarih (İsteğe Bağlı)")
                session_notes = st.text_area("Session Kaydı")
                dm_notes = st.text_area("Session Hakkında DM Notları")
                published = st.checkbox("Oyunculara Yayınla",value=False)
                submitted = st.form_submit_button("💾 Oturumu Kaydet",type="primary")
                if submitted: 
                    ses_title = ses_title.strip()
                    if not ses_title:
                        st.error("Başlık boş olamaz")
                    else:
                        WorldManager.create_session(ses_num,ses_title,date,session_notes,dm_notes,published)
                        st.rerun()
        with st.expander("Toplu Bilgi Gizleme Ayarı"):
            fc1,fc2 = st.columns(2)
            if fc1.button("PC dışındaki tüm kartları kilitle", key="btn_bulk_lock"):
                WorldManager.bulk_set_visibility(only_non_pc=True,visible=False)
                st.rerun()
            if fc2.button("Tüm kartların kilidini aç", key="btn_bulk_rev"):
                WorldManager.bulk_set_visibility(only_non_pc=False,visible=True)
                st.rerun()

    if not sessions:
        st.info("Henüz kaydedilmiş bir session notu bulunmamaktadır.")
        return
    raw_aliases = WikiLinker.buildAliasMap()
    aliases = {k: v for k, v in raw_aliases.items() if is_visible(v)}
    for idx, s in enumerate(reversed(sessions)):
        icon = ("🟢 " if s.is_published else "📝 ") if dm_mode else ""
        date_suffix = f" — 📅 {s.session_date}" if s.session_date else ""
        with st.expander(f"{icon}Session {s.session_number}: {s.title}{date_suffix}", expanded=(idx == 0)):
            st.markdown(renderLinks(s.summary_player,aliases) if s.summary_player else "Özet henüz eklenmemiş",unsafe_allow_html=True)
            if dm_mode and s.dm_notes:
                st.warning("DM Session Notları")
                st.markdown(renderLinks(s.dm_notes, aliases),unsafe_allow_html=True)
            if dm_mode:
                combined_text = (s.summary_player or "") + "\n" + (s.dm_notes or "")
                mentions = WorldManager.analyze_session_mention(combined_text)
                secret_cards = mentions["secret"]
                locked_cards = mentions["locked_details"]
                if secret_cards or locked_cards:
                    with st.expander(f"Oturumda geçen kartlar ({len(secret_cards)} Gizli, {(len(locked_cards))} Kilitli)"):
                        if secret_cards:
                            st.caption("Gizli Kartlar")
                            for ent in secret_cards:
                                c1, c2, c3, c4 = st.columns([3,2,2,1.5])
                                c1.write(f"**{ent.name}**")
                                if c2.button("Kartı Göster(Kısmen)", key=f"rev_base_{s.id}_{ent.id}"):
                                    WorldManager.reveal_entity_to_players(ent.id,full=False)
                                    st.rerun()
                                if c3.button("Kartı göster(Tamamen)",key=f"rev_full_{s.id}_{ent.id}"):
                                    WorldManager.reveal_entity_to_players(ent.id,full=True)
                                    st.rerun()
                                c4.button("Git",key=f"go_sec_{s.id}_{ent.id}", on_click=goTo,args=(ent.name,))
                        if locked_cards:
                            st.caption("Detayları Gizlenmiş Kartlar")
                            for ent in locked_cards:
                                lc1,lc2 = st.columns([4,1.5])
                                lc1.write(f"**{ent.name}**")
                                lc2.button("Ayarla ➔", key=f"go_lock_{s.id}_{ent.id}", on_click=goTo,args=(ent.name,))
                with st.expander("✏️ Düzenle/Sil"):
                    with st.form(f"form_edit_session_{s.id}"):
                        c1, c2 = st.columns([1,3])
                        ses_num = c1.number_input("Session No",min_value=1,value=s.session_number,step=1,key=f"ed_nums_{s.id}")
                        ses_title = c2.text_input("Başlık *", value=s.title,key=f"ed_title_{s.id}")
                        date = st.text_input("Session'ın Oynandığı Tarih (İsteğe Bağlı)",s.session_date,key=f"ed_date_{s.id}")
                        session_notes = st.text_area("Session Kaydı",value=s.summary_player,key=f"ed_note_{s.id}")
                        dm_notes = st.text_area("Session Hakkında DM Notları",s.dm_notes,key=f"ed_dm_note_{s.id}")
                        published = st.checkbox("Oyunculara Yayınla",value=s.is_published,key=f"ed_pub_{s.id}")
                        submitted = st.form_submit_button("💾 Oturumu Kaydet",type="primary")
                        if submitted:
                            ses_title = ses_title.strip()
                            if not ses_title:
                                st.error("Başlık boş olamaz")
                            else:
                                WorldManager.update_session(s.id,session_number=ses_num,title=ses_title,session_date=date,summary_player=session_notes,dm_notes=dm_notes,is_published = published)
                                st.rerun()
                    if st.button("🗑️ Session ı sil.", key=f"del_ses_{s.id}"):
                        WorldManager.delete_session(s.id)
                        st.rerun()






