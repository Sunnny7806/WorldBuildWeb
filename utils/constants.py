import os
import re
from urllib.parse import quote
import streamlit as st

#BU KOD LİNKLERİ BİRBİRİNE BAĞLAMA GÖREVİNİ YAPIYOR.

# Dizinler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_upload_dir() ->str:
    """Aktif olan evrenin upload klasorünü döner."""
    from database import get_active_universe
    from utils.universe import get_universe_dirs
    _, upload_dir = get_universe_dirs(get_active_universe())
    return upload_dir

os.makedirs(get_upload_dir(), exist_ok=True)

# İkonlar ve Regex
LINK_RE = re.compile(r'\[([^\[\]|]+)(?:\|([^\[\]]+))?\]')
TYPE_ICONS = {
    "character": "🧙", 
    "item": "💎", 
    "location": "🏰",
    "god": "⚡",
    "district": "🍺",
    "faction": "🛡️",
    "monster": "🐉"
}


def goTo(name: str):
    """Belirtilen entity adına sahip sayfaya yönlendirir."""
    st.query_params["page"] = name


def renderLinks(text: str, existingNames: set) -> str:
    """[Viladimir] veya [Viladimir|Varis] metinlerini tıklanabilir bağlantılara çevirir."""
    def replace(match):
        target = match.group(1).strip()
        label = match.group(2) or target
        if target in existingNames:
            return f'<a href="?page={quote(target)}" target="_self">{label}</a>'
        return f'<span style="color:#e05555">{label}</span>'
    return LINK_RE.sub(replace, text)


def getDetails(entity) -> dict:
    """Entity'nin türüne göre detay bilgilerini sözlük olarak döner."""
    if entity.character:
        c = entity.character
        details = {
            "Tür": "⭐ Oyuncu (PC)" if getattr(c, 'is_player', False) else "🎭 NPC",
            "Irk": c.race,
            "Sınıf": c.char_class,
            "Seviye": str(getattr(c, 'level', 1) or 1),
            "Can (HP)": f"{getattr(c, 'hp_current', 10)} / {getattr(c, 'hp_max', 10)}",
            "Zırh (AC)": str(getattr(c, 'armor_class', 10) or 10),
            "Yönelim": c.alignment
        }
        if getattr(c, 'is_player', False) and getattr(c, 'player_name', ''):
            details["Oynayan"] = c.player_name
        if c.faction_id:
            from worldManager import WorldManager
            f_ent = WorldManager.getEntityById(c.faction_id)
            if f_ent:
                details["Bağlı Olduğu Lonca"] = f"{f_ent.name} ({c.faction_role})" if c.faction_role else f_ent.name
        return details
    
    if entity.item:
        i = entity.item
        details = {"Tür": i.item_type, "Nadirlik": i.rarity, "Değer": i.value, "Özellik": i.specialS}
        if i.owner_id:
            from worldManager import WorldManager
            owner = WorldManager.getEntityById(i.owner_id)
            if owner:
                details["Sahibi"] = owner.name
        if i.location_id:
            from worldManager import WorldManager
            loc = WorldManager.getEntityById(i.location_id)
            if loc:
                details["Bulunduğu Yer"] = loc.name
        return details
    
    if entity.location:
        l = entity.location
        return {"Nüfus": l.population, "Din": l.religion, "İklim": l.climate, "Yönetici": l.ruler}
    
    if entity.god:
        g = entity.god
        return {"Yönelim": g.alignment, "Etki Alanı": g.domain, "Sembol": g.symbol}
    
    if entity.district:
        d = entity.district
        details = {"Mekan Türü": d.district_type, "Sahibi/Lideri": d.ruler_or_owner}
        if d.parent_location_id:
            from worldManager import WorldManager
            parent = WorldManager.getEntityById(d.parent_location_id)
            if parent:
                details["Bağlı Olduğu Şehir"] = parent.name
        return details
    
    if entity.faction:
        f = entity.faction
        return {"Lonca Türü": f.faction_type, "Lider": f.leader, "Merkez": f.headquarters, "Motto": f.motto, "Yönelim": f.alignment}

    if entity.monster:
        m = entity.monster
        return {
            "Zorluk (CR)": f"CR {m.cr}",
            "Tür & Boyut": f"{m.size} {m.monster_type}",
            "Zırh (AC)": str(m.armor_class or 10),
            "Can (HP)": f"{m.hp_max} HP",
            "Hız": m.speed or "30 ft"
        }

    return {}
