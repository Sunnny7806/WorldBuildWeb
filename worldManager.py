from database import SessionLocal, get_db, Entity, Character, Item, Location, EntityLink, God, District, MapPin, Faction, Monster
from sqlalchemy.orm import joinedload

# Tüm alt tabloları tek seferde yüklemek için merkezi ilişki listesi:
ENTITY_LOAD_OPTIONS = [
    joinedload(Entity.character),
    joinedload(Entity.item),
    joinedload(Entity.location),
    joinedload(Entity.god),
    joinedload(Entity.district),
    joinedload(Entity.faction),
    joinedload(Entity.monster)
]

#EKLEME ÇIKARTMA GİBİ BİR ÇOK FONKSİYONU BARINDIRAN BACKEND İN BULUNDUĞU KOD.


class WorldManager:
    # ==========================================
    # 1. OLUŞTURMA İŞLEMLERİ (CREATE)
    # ==========================================

    @staticmethod
    def create_character(
        name: str, race: str, char_class: str, alignment: str,
        faction_id: str = None, faction_role: str = "",
        is_player: bool = False, player_name: str = "", level: int = 1,
        hp_current: int = 10, hp_max: int = 10, armor_class: int = 10, speed: str = "30 ft",
        stats_json: str = None, spells_and_features: str = "",
        aliases: str = "", content_md: str = "", image_path: str = ""
    ):
        with get_db() as db:
            default_stats = '{"STR":10,"DEX":10,"CON":10,"INT":10,"WIS":10,"CHA":10}'
            char_stats = Character(
                race=race, char_class=char_class, alignment=alignment,
                faction_id=faction_id, faction_role=faction_role,
                is_player=is_player, player_name=player_name, level=level,
                hp_current=hp_current, hp_max=hp_max, armor_class=armor_class, speed=speed,
                stats_json=stats_json or default_stats,
                spells_and_features=spells_and_features
            )
            entity = Entity(
                name=name, aliases=aliases, entity_type="character",
                content_md=content_md, image_path=image_path, character=char_stats
            )
            db.add(entity)
            db.flush()
            _ = entity.character
            return entity

    @staticmethod
    def create_item(name: str, item_type: str, rarity: str, value: str = "", specialS: str = "", owner_id:str=None, location_id:str=None, aliases: str = "", content_md: str = "", image_path: str = ""):
        with get_db() as db:
            item_stats = Item(item_type=item_type, rarity=rarity, value=value, specialS=specialS, owner_id=owner_id, location_id=location_id)
            entity = Entity(
                name=name, aliases=aliases, entity_type="item",
                content_md=content_md, image_path=image_path, item=item_stats
            )
            db.add(entity)
            db.flush()
            _ = entity.item
            return entity

    @staticmethod
    def create_location(name: str, population: str, religion: str, climate: str, ruler: str, aliases: str = "", content_md: str = "", image_path: str = ""):
        with get_db() as db:
            location_info = Location(population=population, religion=religion, climate=climate, ruler=ruler)
            entity = Entity(
                name=name, aliases=aliases, entity_type="location",
                content_md=content_md, image_path=image_path, location=location_info
            )
            db.add(entity)
            db.flush()
            _ = entity.location
            return entity

    @staticmethod
    def create_god(name: str, alignment: str, domain: str, symbol: str = "", aliases: str = "", content_md: str = "", image_path: str = ""):
        with get_db() as db:
            god_info = God(alignment=alignment, domain=domain, symbol=symbol)
            entity = Entity(
                name=name, aliases=aliases, entity_type="god",
                content_md=content_md, image_path=image_path, god=god_info
            )
            db.add(entity)
            db.flush()
            _ = entity.god
            return entity

    @staticmethod
    def create_district(name: str, parent_location_id: str, district_type: str, ruler_or_owner: str = "", aliases: str = "", content_md: str = "", image_path: str = ""):
        with get_db() as db:
            district_info = District(
                parent_location_id=parent_location_id,
                district_type=district_type,
                ruler_or_owner=ruler_or_owner
            )
            entity = Entity(
                name=name, aliases=aliases, entity_type="district",
                content_md=content_md, image_path=image_path, district=district_info
            )
            db.add(entity)
            db.flush()

            # Şehir ile bu mekan arasına çift taraflı Wiki linki ekle
            if parent_location_id:
                db.add(EntityLink(source_id=parent_location_id, target_id=entity.id))
                db.add(EntityLink(source_id=entity.id, target_id=parent_location_id))

            _ = entity.district
            return entity

    @staticmethod
    def create_faction(name:str, faction_type:str, leader:str="", headquarters:str="", motto:str="", alignment:str="", aliases:str="", content_md:str="", image_path:str=""):
        with get_db() as db:
            faction_info = Faction(faction_type=faction_type, leader=leader, headquarters=headquarters, motto=motto, alignment=alignment)
            entity = Entity(name=name, aliases=aliases, entity_type="faction",
                            content_md=content_md, image_path=image_path, faction=faction_info)
            db.add(entity)
            db.flush()
            _ = entity.faction
            return entity

    @staticmethod
    def create_monster(
        name: str, cr: str = "1", monster_type: str = "İnsansı", size: str = "Orta",
        armor_class: int = 10, hp_max: int = 10, speed: str = "30 ft",
        stats_json: str = None, actions_json: str = None, traits: str = "",
        aliases: str = "", content_md: str = "", image_path: str = ""
    ):
        with get_db() as db:
            default_stats = '{"STR":10,"DEX":10,"CON":10,"INT":10,"WIS":10,"CHA":10}'
            monster_stats = Monster(
                cr=cr, monster_type=monster_type, size=size,
                armor_class=armor_class, hp_max=hp_max, speed=speed,
                stats_json=stats_json or default_stats,
                actions_json=actions_json or "[]",
                traits=traits
            )
            entity = Entity(
                name=name, aliases=aliases, entity_type="monster",
                content_md=content_md or f"# {name}\n\nCR {cr} seviyesinde bir {monster_type}.",
                image_path=image_path, monster=monster_stats
            )
            db.add(entity)
            db.flush()
            _ = entity.monster
            return entity

    # ==========================================
    # 2. OKUMA VE ARAMA İŞLEMLERİ (READ / SEARCH)
    # ==========================================

    @staticmethod
    def get_all_entities():
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).all()

    @staticmethod
    def getEntityByName(name: str):
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).filter(Entity.name == name).first()

    @staticmethod
    def getEntityById(entity_id: str):
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).filter(Entity.id == entity_id).first()

    @staticmethod
    def getDistrictsOfLocation(location_id: str):
        """Bir şehre bağlı tüm alt mekanları (bar, pazar vb.) getirir."""
        with get_db() as db:
            return db.query(Entity).join(District, District.entity_id == Entity.id).filter(
                District.parent_location_id == location_id
            ).all()

    @staticmethod
    def get_faction_members(faction_id: str):
        """Bir loncaya bağlı tüm karakterleri getirir."""
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).join(Character, Character.entity_id == Entity.id).filter(Character.faction_id == faction_id).all()

    @staticmethod
    def get_character_inventory(character_id:str):
        """Bir karaktere ait tüm eşyaları getirir."""
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).join(Item, Item.entity_id == Entity.id).filter(Item.owner_id == character_id).all()

    @staticmethod
    def get_location_inventory(location_id:str):
        """Bir markette veya dükkanda bulunan eşyaları getirir."""
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).join(Item, Item.entity_id == Entity.id).filter(Item.location_id == location_id).all()    

    @staticmethod
    def bulk_add_faction_members(faction_id:str, roster:list[dict]):
        """Üretilen kadroyu topluca Character olarak veritabanına ekler."""
        with get_db() as db:
            created = []
            for member in roster:
                name = member.get("name", "").strip()
                role = member.get("role", "").strip()
                if not name:
                    continue
                char_stats = Character(race="Bilinmiyor", char_class="NPC", alignment="Tarafsız", faction_id=faction_id, faction_role=role)
                entity = Entity(name=name, entity_type="character", content_md=f"{name} bu loncanın bir üyesidir.", character=char_stats)
                db.add(entity)
                created.append(entity)
            db.flush()
            return created

    @staticmethod
    def update_character_hp(character_id: str, delta: int):
        """Karakterin canını delta kadar artırır/azaltır. (0 ile hp_max arasında sınırlar)."""
        with get_db() as db:
            char = db.query(Character).filter(Character.entity_id == character_id).first()
            if char:
                max_hp = char.hp_max or 10
                current = char.hp_current if char.hp_current is not None else max_hp
                char.hp_current = max(0, min(max_hp, current + delta))
                db.flush()
                return char.hp_current
            return None

    @staticmethod
    def get_modifier(score: int) -> str:
        """16 gibi bir stat skorundan '+3', 8 için '-1' modifikatör üretir."""
        mod = (score - 10) // 2
        return f"+{mod}" if mod >= 0 else str(mod)

    @staticmethod
    def get_characters_by_player_status(is_player: bool):
        """Sadece oyuncuları veya sadece NPC'leri getirir."""
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).join(Character, Character.entity_id == Entity.id).filter(
                Character.is_player == is_player
            ).all()

    @staticmethod
    def get_all_monsters():
        """Tüm canavarları döner."""
        with get_db() as db:
            return db.query(Entity).options(*ENTITY_LOAD_OPTIONS).filter(Entity.entity_type == "monster").all()

    @staticmethod
    def import_srd_monster(monster_data: dict):
        """Hazır bir SRD canavarını veritabanına ekler (eğer yoksa)."""
        import json
        m_name = monster_data["name"]
        existing = WorldManager.getEntityByName(m_name)
        if existing:
            return existing

        stats_json = json.dumps(monster_data.get("stats", {}))
        actions_json = json.dumps(monster_data.get("actions", []))
        return WorldManager.create_monster(
            name=m_name,
            cr=monster_data.get("cr", "1"),
            monster_type=monster_data.get("monster_type", "Canavar"),
            size=monster_data.get("size", "Orta"),
            armor_class=monster_data.get("armor_class", 10),
            hp_max=monster_data.get("hp_max", 10),
            speed=monster_data.get("speed", "30 ft"),
            stats_json=stats_json,
            actions_json=actions_json,
            traits=monster_data.get("traits", ""),
            content_md=f"# {m_name}\n\n**CR {monster_data.get('cr', '1')}** — {monster_data.get('size', 'Orta')} {monster_data.get('monster_type', 'Canavar')}\n\n{monster_data.get('traits', '')}"
        )


    @staticmethod
    def search(keyword: str):
        with get_db() as db:
            pattern = f"%{keyword}%"
            return db.query(Entity).filter(
                (Entity.name.ilike(pattern)) | (Entity.aliases.ilike(pattern))
            ).all()

    # ==========================================
    # 3. GÜNCELLEME VE SİLME (UPDATE / DELETE)
    # ==========================================

    @staticmethod
    def updateEntity(entity_id: str, **fields):
        with get_db() as db:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                print("Güncellenecek varlık bulunamadı.")
                return None

            sub_models = [entity.character, entity.item, entity.location, entity.god, entity.district, entity.faction, entity.monster]

            for key, value in fields.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
                else:
                    updated_in_sub = False
                    for sub in sub_models:
                        if sub and hasattr(sub, key):
                            setattr(sub, key, value)
                            updated_in_sub = True
                            break
                    if not updated_in_sub:
                        print(f"Uyarı: '{key}' alanı bulunamadı, atlandı.")

            db.flush()
            db.refresh(entity)
            return entity

    @staticmethod
    def deleteEntity(entity_id: str) -> bool:
        with get_db() as db:
            entity = db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                return False

            # Bağlı tüm harita pinlerini ve wiki linklerini temizle
            db.query(EntityLink).filter(
                (EntityLink.source_id == entity_id) | (EntityLink.target_id == entity_id)
            ).delete()
            db.query(MapPin).filter(
                (MapPin.target_entity_id == entity_id) | (MapPin.location_id == entity_id)
            ).delete()

            db.delete(entity)
            return True

    # ==========================================
    # 4. HARİTA PİNLERİ (MAP PINS)
    # ==========================================

    @staticmethod
    def add_map_pin(map_type: str, target_entity_id: str, x: float, y: float, location_id: str = None, label: str = ""):
        with get_db() as db:
            pin = MapPin(
                map_type=map_type,
                target_entity_id=target_entity_id,
                location_id=location_id,
                x=round(float(x), 2),
                y=round(float(y), 2),
                label=label
            )
            db.add(pin)
            db.flush()
            db.refresh(pin)
            return pin

    @staticmethod
    def get_map_pins(map_type: str, location_id: str = None):
        with get_db() as db:
            query = db.query(MapPin, Entity).join(Entity, Entity.id == MapPin.target_entity_id)
            if map_type == "world":
                query = query.filter(MapPin.map_type == "world")
            else:
                query = query.filter(MapPin.map_type == "location", MapPin.location_id == location_id)
            return query.all()

    @staticmethod
    def delete_map_pin(pin_id: str):
        with get_db() as db:
            pin = db.query(MapPin).filter(MapPin.id == pin_id).first()
            if pin:
                db.delete(pin)
                return True
            return False
