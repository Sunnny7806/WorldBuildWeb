import copy
import json
from types import SimpleNamespace
import streamlit as st
from database import SessionLocal, get_db, get_active_universe, Entity, Character, Item, Location, EntityLink, God, District, MapPin, Faction, Monster, Lore, EncounterState
from sqlalchemy.orm import joinedload
# Tüm alt tabloları tek seferde yüklemek için merkezi ilişki listesi:
ENTITY_LOAD_OPTIONS = [
    joinedload(Entity.character),
    joinedload(Entity.item),
    joinedload(Entity.location),
    joinedload(Entity.god),
    joinedload(Entity.district),
    joinedload(Entity.faction),
    joinedload(Entity.monster),
    joinedload(Entity.lore)
]


@st.cache_data(ttl=300, show_spinner=False)
def _cached_entity_summaries(universe_name: str) -> list[dict]:
    """Sol menü, sayaçlar ve link haritası için sade varlık özetlerini önbellekler."""
    with get_db(universe_name) as db:
        rows = (
            db.query(
                Entity.id,
                Entity.name,
                Entity.aliases,
                Entity.entity_type,
                Entity.is_secret,
                Character.is_player,
            )
            .outerjoin(Character, Character.entity_id == Entity.id)
            .all()
        )
        return [
            {
                "id": r[0],
                "name": r[1],
                "aliases": r[2] or "",
                "entity_type": r[3],
                "is_secret": bool(r[4]),
                "is_player": bool(r[5]) if r[5] is not None else False,
            }
            for r in rows
        ]


@st.cache_data(ttl=300, show_spinner=False)
def _cached_map_pins(universe_name: str, map_type: str, location_id: str | None, include_secret: bool) -> list[tuple[dict, dict]]:
    """Harita pinlerini düz veri olarak önbellekler."""
    with get_db(universe_name) as db:
        query = db.query(MapPin, Entity).join(Entity, Entity.id == MapPin.target_entity_id)
        if not include_secret:
            query = query.filter(Entity.is_secret.is_not(True))
        if map_type == "world":
            query = query.filter(MapPin.map_type == "world")
        else:
            query = query.filter(MapPin.map_type == "location", MapPin.location_id == location_id)
        return [
            (
                {"id": p.id, "x": p.x, "y": p.y, "label": p.label or ""},
                {"name": e.name, "entity_type": e.entity_type},
            )
            for p, e in query.all()
        ]


@st.cache_data(ttl=300, show_spinner=False)
def _cached_encounter(universe_name: str) -> dict:
    """Aktif savaş durumunu önbellekten okur."""
    with get_db(universe_name) as db:
        encounter = db.query(EncounterState).filter(EncounterState.id == 1).first()
        if not encounter:
            return {"is_active": False, "round": 1, "turn_idx": 0, "combatants": [], "last_roll": ""}
        combat = json.loads(encounter.combatants_json or "[]")
        return {
            "is_active": encounter.is_active,
            "round": encounter.round_num,
            "turn_idx": encounter.turn_idx,
            "combatants": combat,
            "last_roll": encounter.last_roll or "",
        }


@st.cache_data(ttl=300, show_spinner=False)
def _cached_backlinks(universe_name: str, entity_id: str) -> list[dict]:
    """Bir sayfaya verilen backlink özetlerini önbellekler."""
    with get_db(universe_name) as db:
        rows = (
            db.query(Entity.id, Entity.name, Entity.entity_type, Entity.is_secret)
            .join(EntityLink, EntityLink.source_id == Entity.id)
            .filter(EntityLink.target_id == entity_id)
            .all()
        )
        return [
            {"id": r[0], "name": r[1], "entity_type": r[2], "is_secret": bool(r[3])}
            for r in rows
        ]


#EKLEME ÇIKARTMA GİBİ BİR ÇOK FONKSİYONU BARINDIRAN BACKEND İN BULUNDUĞU KOD.


class WorldManager:
    @staticmethod
    def clear_cache():
        """Yazma işlemlerinden sonra okuma önbelleklerini temizler."""
        _cached_entity_summaries.clear()
        _cached_map_pins.clear()
        _cached_encounter.clear()
        _cached_backlinks.clear()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
            return entity

    @staticmethod
    def create_lore(name: str, category: str = "Evren Bilgisi", era: str = "", aliases: str = "", content_md: str = "", image_path: str = ""):
        with get_db() as db:
            lore_stats = Lore(category=category, era=era)
            entity = Entity(
                name=name, aliases=aliases, entity_type="lore",
                content_md=content_md or f"# {name}\n\n{category}",
                image_path=image_path, lore=lore_stats
            )
            db.add(entity)
            db.flush()
            _ = entity.lore
            WorldManager.clear_cache()
            return entity

    # ==========================================
    # 2. OKUMA VE ARAMA İŞLEMLERİ (READ / SEARCH)
    # ==========================================

    @staticmethod
    def get_entity_summaries(include_secret: bool = True):
        """Sol menü, sayaçlar ve link haritası için hafif önbellekli liste döner."""
        rows = _cached_entity_summaries(get_active_universe())
        items = [SimpleNamespace(**r) for r in rows]
        if not include_secret:
            return [e for e in items if not e.is_secret]
        return items

    @staticmethod
    def search_summaries(keyword: str, include_secret: bool = True):
        """Önbellekli özet listede isim ve takma ad araması yapar."""
        items = WorldManager.get_entity_summaries(include_secret=include_secret)
        if not keyword:
            return items
        kw = keyword.lower()
        return [e for e in items if kw in e.name.lower() or kw in e.aliases.lower()]

    @staticmethod
    def get_backlinks(entity_id: str):
        """Bir sayfaya bağlantı veren varlıkların özetlerini önbellekten döner."""
        rows = _cached_backlinks(get_active_universe(), entity_id)
        return [SimpleNamespace(**r) for r in rows]

    @staticmethod
    def get_all_entities(include_secret: bool = True):
        with get_db() as db:
            query =  db.query(Entity).options(*ENTITY_LOAD_OPTIONS)
            if not include_secret: 
                query = query.filter(Entity.is_secret.is_not(True))
            return query.all()

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
            WorldManager.clear_cache()
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
                WorldManager.clear_cache()
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
    def search(keyword: str, include_secret: bool = True):
        with get_db() as db:
            pattern = f"%{keyword}%"
            query = db.query(Entity).options(*ENTITY_LOAD_OPTIONS).filter((Entity.name.ilike(pattern)) | (Entity.aliases.ilike(pattern)))
            if not include_secret:
                query = query.filter(Entity.is_secret.is_not(True))
            return query.all()

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

            sub_models = [entity.character, entity.item, entity.location, entity.god, entity.district, entity.faction, entity.monster, entity.lore]

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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
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
            WorldManager.clear_cache()
            return pin

    @staticmethod
    def get_map_pins(map_type: str, location_id: str = None, include_secret: bool = True):
        raw_pins = _cached_map_pins(get_active_universe(), map_type, location_id, include_secret)
        return [(SimpleNamespace(**p), SimpleNamespace(**e)) for p, e in raw_pins]

    @staticmethod
    def delete_map_pin(pin_id: str):
        with get_db() as db:
            pin = db.query(MapPin).filter(MapPin.id == pin_id).first()
            if pin:
                db.delete(pin)
                WorldManager.clear_cache()
                return True
            return False

    @staticmethod
    def get_encounter():
        return copy.deepcopy(_cached_encounter(get_active_universe()))

    @staticmethod
    def save_encounter(enc_dict:dict):
        with get_db() as db:
            row = db.query(EncounterState).filter(EncounterState.id == 1).first()
            if not row:
                row = EncounterState(id = 1)
                db.add(row)
            row.is_active = enc_dict.get("is_active", False)
            row.round_num = enc_dict.get("round", 1)
            row.turn_idx = enc_dict.get("turn_idx",0)
            row.last_roll = str(enc_dict.get("last_roll",""))
            row.combatants_json = json.dumps(enc_dict.get("combatants", []))
            db.flush()
            WorldManager.clear_cache()
            return row   


        