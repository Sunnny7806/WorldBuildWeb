from database import SessionLocal, Entity, EntityLink
from worldManager import WorldManager
from linker import WikiLinker

#ENTİTYLERİ BİRBİRLERİYLE BAĞLAYAN KOD.


class BacklinkManager:
    @staticmethod
    def syncLinks(entity_id: str):
        """Bir sayfanın metnini okuyup entity_links tablosunu günceller."""
        db = SessionLocal()
        try:
            entity = db.get(Entity, entity_id)
            if not entity:
                return

            names = WikiLinker.extractLinks(entity.content_md or "")

            # Eski linkleri sil, sıfırdan yaz
            db.query(EntityLink).filter(EntityLink.source_id == entity_id).delete()

            if names:
                targets = db.query(Entity).filter(Entity.name.in_(names)).all()
                for target in targets:
                    if target.id != entity_id:   # sayfa kendine link vermesin
                        db.add(EntityLink(source_id=entity_id, target_id=target.id))

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Hata! Linkler senkronize edilemedi: {e}")
        finally:
            db.close()

    @staticmethod
    def getBacklinks(entity_id: str):
        """Bu sayfaya link veren sayfaları döndürür."""
        db = SessionLocal()
        try:
            return (
                db.query(Entity)
                .join(EntityLink, EntityLink.source_id == Entity.id)
                .filter(EntityLink.target_id == entity_id)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def saveContent(entity_id: str, text: str, auto_link: bool = True):
        """Metni (isteğe bağlı) linkler, kaydeder ve link tablosunu günceller."""
        if auto_link:
            text = WikiLinker.autoLink(text)
        WorldManager.updateEntity(entity_id, content_md=text)
        BacklinkManager.syncLinks(entity_id)

    @staticmethod
    def syncAll():
        """Var olan tüm sayfaların linklerini baştan hesaplar."""
        for e in WorldManager.get_all_entities():
            BacklinkManager.syncLinks(e.id)