from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey,Boolean, Integer, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import uuid
from datetime import datetime
from contextlib import contextmanager
from utils.universe import get_universe_dirs

#ENTİTY CLASS LARININ OLUŞTUĞU İLK KISIM.

_CURRENT_UNIVERSE = "Asterfall"
_ENGINES = {}
_SESSION_FACTORIES = {}

def set_active_universe(name: str):
    """Aktif evreni değiştirir."""
    global _CURRENT_UNIVERSE
    _CURRENT_UNIVERSE = name

def get_active_universe() ->str:
    """O an aktif olan evren adını döner."""
    return _CURRENT_UNIVERSE

def _run_migrations(engine):
    """Mevcut evren veritabanlarında yeni eklenen sütunları kontrol eder ve eksikse ekler."""
    with engine.connect() as conn:
        migrations = [
            "ALTER TABLE characters ADD COLUMN faction_id VARCHAR",
            "ALTER TABLE characters ADD COLUMN faction_role VARCHAR",
            "ALTER TABLE items ADD COLUMN owner_id VARCHAR",
            "ALTER TABLE items ADD COLUMN location_id VARCHAR",
             # Aşama 3: Oyuncu ve Character Sheet Sütunları
            "ALTER TABLE characters ADD COLUMN is_player BOOLEAN DEFAULT 0",
            "ALTER TABLE characters ADD COLUMN player_name VARCHAR DEFAULT ''",
            "ALTER TABLE characters ADD COLUMN level INTEGER DEFAULT 1",
            "ALTER TABLE characters ADD COLUMN hp_current INTEGER DEFAULT 10",
            "ALTER TABLE characters ADD COLUMN hp_max INTEGER DEFAULT 10",
            "ALTER TABLE characters ADD COLUMN armor_class INTEGER DEFAULT 10",
            "ALTER TABLE characters ADD COLUMN speed VARCHAR DEFAULT '30 ft'",
            "ALTER TABLE characters ADD COLUMN stats_json VARCHAR DEFAULT ''",
            "ALTER TABLE characters ADD COLUMN spells_and_features TEXT DEFAULT ''",
        ]
        for query in migrations:
            try:
                conn.execute(text(query))
                conn.commit()
            except Exception:
                # Sütun zaten varsa SQLite hata verir; bunu güvenle görmezden geliyoruz.
                pass

def get_engine(universe_name: str = None):
    """Belirtilen evrenin veritabanı motorunu döner. Yoksa tabloları otomatik olarak oluşturur."""
    u_name = universe_name or _CURRENT_UNIVERSE
    if u_name not in _ENGINES:
        db_path, _ = get_universe_dirs(u_name)
        engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(engine)
        _run_migrations(engine)
        _ENGINES[u_name] = engine
        _SESSION_FACTORIES[u_name] = sessionmaker(autocommit=False, autoflush=False,expire_on_commit=False, bind=engine)
    return _ENGINES[u_name]

def get_session_factory(universe_name:str = None):
    u_name = universe_name or _CURRENT_UNIVERSE
    if u_name not in _SESSION_FACTORIES:
        get_engine(u_name)
    return _SESSION_FACTORIES[u_name]

def SessionLocal():
    """Eski kodlar hata vermesin diye"""
    return get_session_factory()()


@contextmanager
def get_db(universe_name:str = None):
    """Aktif evrenin veritabanını açar. İşlem bitincce otomatik kaydeder ve kapatır."""
    factory = get_session_factory(universe_name)
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


Base = declarative_base()

# 3. Entities (Varlıklar) Tablosu
class Entity(Base):
    __tablename__ = "entities"

    # Sütunlarımızı tanımlıyoruz
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    aliases = Column(String, default="")
    entity_type = Column(String, nullable=False) # 'character', 'item', 'location' vb.
    content_md = Column(String, default="")
    image_path = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    character = relationship("Character", foreign_keys="Character.entity_id", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    item = relationship("Item", foreign_keys="Item.entity_id", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    location = relationship("Location", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    god = relationship("God", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    district = relationship("District", foreign_keys="District.entity_id", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    faction = relationship("Faction", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    monster = relationship("Monster", foreign_keys="Monster.entity_id", back_populates="entity", uselist=False, cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key = True)

    race = Column(String)
    char_class = Column(String)
    alignment = Column(String)
    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="character")
    faction_id = Column(String, ForeignKey("entities.id"), nullable=True)
    faction_role = Column(String, default="")

    # --- AŞAMA 3: OYUNCU & STAT BLOCK ALANLARI ---
    is_player = Column(Boolean, default=False)
    player_name = Column(String, default="")
    level = Column(Integer, default=1)
    hp_current = Column(Integer, default=10)
    hp_max = Column(Integer, default=10)
    armor_class = Column(Integer, default=10)
    speed = Column(String, default="30 ft")
    stats_json = Column(String, default='{"STR":10,"DEX":10,"CON":10,"INT":10,"WIS":10,"CHA":10}')
    spells_and_features = Column(String, default="")

class Item(Base):
    __tablename__= "items"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key=True)

    item_type = Column(String)
    rarity = Column(String)
    value = Column(String)
    specialS = Column(String)
    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="item")
    owner_id = Column(String, ForeignKey("entities.id"), nullable=True)
    location_id = Column(String, ForeignKey("entities.id"), nullable=True)

class Location(Base):
    __tablename__ = "locations"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key=True)

    population = Column(String)
    religion = Column(String)
    climate = Column(String)
    ruler = Column(String)
    map_image_path = Column(String, default="")  # Şehrin kendi harita görseli
    entity = relationship("Entity", back_populates="location")

class God(Base):
    __tablename__ = "gods"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key=True)

    alignment = Column(String)  # Yönelim (Örn: Kaotik İyi, Tarafsız)
    domain = Column(String)     # Alanı (Örn: Savaş, Fırtına, Işık, Ölüm)
    symbol = Column(String)     # Kutsal Sembolü (Örn: Kırık Kılıç, Güneş)
    entity = relationship("Entity", back_populates="god")

class District(Base):
    __tablename__ = "districts"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key=True)
    parent_location_id = Column(String, ForeignKey("entities.id"), nullable=True)  # Hangi şehre bağlı olduğu!

    district_type = Column(String)  # Türü (Örn: Bar/Taverna, Pazar, Askeri Bölge, Tapınak)
    ruler_or_owner = Column(String) # Sahibi / İşletmecisi / Lonca Başı
    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="district")

class Faction(Base):
    __tablename__ = "factions"
    entity_id = Column(String,ForeignKey("entities.id"),primary_key=True)
    
    faction_type = Column(String)
    leader = Column(String)
    headquarters = Column(String)
    motto = Column(String)
    alignment = Column(String)

    entity = relationship("Entity", back_populates="faction")

class Monster(Base):
    __tablename__ = "monsters"
    entity_id = Column(String, ForeignKey("entities.id"), primary_key=True)

    cr = Column(String, default="1")  # Challenge Rating (Örn: "1/4", "1/2", "3")
    monster_type = Column(String, default="İnsansı")  # Tür (Canavar, Ejderha, Hortlak, Hayvan vb.)
    size = Column(String, default="Orta")  # Boyut (Küçük, Orta, Büyük, Dev)
    armor_class = Column(Integer, default=10)
    hp_max = Column(Integer, default=10)
    speed = Column(String, default="30 ft")
    stats_json = Column(String, default='{"STR":10,"DEX":10,"CON":10,"INT":10,"WIS":10,"CHA":10}')
    actions_json = Column(String, default='[]')  # Saldırılar ve hasarlar listesi
    traits = Column(String, default="")  # Özel nitelikler / pasifler

    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="monster")


class EntityLink(Base):
    __tablename__ = "entity_links"

    source_id = Column(String, ForeignKey("entities.id"), primary_key=True)
    target_id = Column(String, ForeignKey("entities.id"), primary_key=True)

class MapPin(Base):
    __tablename__ = "map_pins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    map_type = Column(String, nullable=False)  # "world" (dünya haritası) veya "location" (şehir haritası)
    location_id = Column(String, ForeignKey("entities.id"), nullable=True)  # Eğer şehir haritasıysa hangi şehrin haritası?
    target_entity_id = Column(String, ForeignKey("entities.id"), nullable=False)  # Tıklanınca açılacak entity (Şehir veya Bar)
    x = Column(Float, nullable=False)  # Yüzde cinsinden X konumu (0 - 100)
    y = Column(Float, nullable=False)  # Yüzde cinsinden Y konumu (0 - 100)
    label = Column(String, default="") # Pin üzerinde görünecek isim