import random

# 1. Geniş Fantastik İsim Havuzu (Yaklaşık 70+ İsim)
FIRST_NAMES = [
    # Gizemli / Çevik
    "Corin", "Jax", "Sylas", "Marek", "Kaelen", "Varis", "Dante", "Nyx", "Zephyr", "Riven",
    "Lyra", "Vespera", "Elenor", "Sariel", "Talia", "Kira", "Morrigan", "Raven", "Faye", "Shade",
    # Güçlü / Şövalye / Savaşçı
    "Valen", "Gareth", "Bryn", "Roderick", "Theron", "Alden", "Garrick", "Torin", "Krag", "Dorn",
    "Gwendolyn", "Valeria", "Brangwin", "Morwen", "Astrid", "Eldrid", "Hilda", "Sigrid", "Rowena",
    # Bilge / Mistik / Büyüsel
    "Archibald", "Aethelgard", "Balthazar", "Ignis", "Caelum", "Oryon", "Severus", "Xander", "Eldrin",
    "Celeste", "Morgana", "Yvaine", "Althea", "Isolde", "Seraphina", "Nocturna", "Astra", "Lunara",
    # Kurnaz / Tüccar / Sokak
    "Barnaby", "Finch", "Pip", "Tobias", "Gideon", "Milo", "Casper", "Felix", "Jasper", "Otis"
]

# 2. Lonca Türlerine Göre Lakaplar ve Rol Hiyerarşileri
THEMES = {
    "thieves_guild": {
        "prefixes": ["Gölge", "Fısıltı", "Sessizadım", "Gecegözü", "Hançer", "Kilitkıran", "Tilkigöz", "Çevikparmak", "Duman"],
        "roles": [
            "Gölge Ustası (Lider Yardımcısı)",
            "Kıdemli Suikastçı",
            "Kilit ve Kasa Uzmanı",
            "Çit (Kaçak Eşya Tüccarı)",
            "Şehir Muhbiri / Casus",
            "Yankesici / Sokak Gözcüsü",
            "Acemi Hırsız (Çaylak)"
        ]
    },
    "mage_academy": {
        "prefixes": ["Yıldızfısıltısı", "Alevbükücü", "Rünbilen", "Kadim", "Külçağıran", "Gökdokuyan", "Zamanbekçisi", "Sırkatibi"],
        "roles": [
            "Başbüyücü Vekili",
            "Kadim Arşividar",
            "Yüksek Simyager",
            "Rün Muhafızı",
            "İllüzyonist / Haberci",
            "Laboratuvar Asistanı",
            "Akademi İnisiyesi (Öğrenci)"
        ]
    },
    "knight_order": {
        "prefixes": ["Demirbilek", "Kurtkan", "Tunçkalkan", "Fırtınayürek", "Akçelik", "Yemintutan", "Kayaomuz", "Aslanyele"],
        "roles": [
            "Büyük Kumandan Yardımcısı",
            "Sancaktar Şövalye",
            "Usta Silahşor / Demirci",
            "Kıdemli Zırhlı Süvari",
            "Gözcü Kolcusu",
            "Saha Sıhhiyecisi",
            "Silahdar (Yaver)"
        ]
    },
    "religious_cult": {
        "prefixes": ["Kutsanmış", "Günahkar", "Karanlıkruh", "Işıkgöz", "Kefaret", "Fani", "Görümcü", "Alevsaçan"],
        "roles": [
            "Baş Kâhin / Engizisyoncu",
            "Kutsal Emanet Muhafızı",
            "Kefaret Dağıtıcı",
            "Görümcü Rahip",
            "Fanatik Muhafız",
            "Ayin Hizmetkarı",
            "Adanmış Mürit"
        ]
    },
    "merchant_syndicate": {
        "prefixes": ["Altınel", "Gümüşdil", "Kervancı", "Tartıcı", "İpekyol", "Denizkurdu", "Borsacı", "Kurnaz"],
        "roles": [
            "Lonca Saymanı (Kasa Başı)",
            "Kervan Başı",
            "Baş Eksper / Değerleme Uzmanı",
            "Gümrük Komisyoncusu",
            "Korumalar Şefi",
            "Sevkiyat Katibi",
            "Çırak Tüccar"
        ]
    }
}


def _get_theme_key(faction_type: str) -> str:
    """Girilen lonca türü metnine göre en uygun temayı eşleştirir."""
    f_lower = (faction_type or "").lower()
    if any(k in f_lower for k in ["hırsız", "suikast", "haydut", "gölge", "thief", "rogue"]):
        return "thieves_guild"
    elif any(k in f_lower for k in ["büyü", "akademi", "ilim", "mage", "wizard", "arkana"]):
        return "mage_academy"
    elif any(k in f_lower for k in ["şövalye", "ordu", "asker", "muhafız", "paralı", "knight"]):
        return "knight_order"
    elif any(k in f_lower for k in ["tarikat", "dini", "tapınak", "kült", "cult", "kilise"]):
        return "religious_cult"
    else:
        return "merchant_syndicate"


def generate_roster(faction_type: str, count: int = 5) -> list[dict]:
    """
    Belirtilen lonca türüne göre mantıklı rol hiyerarşisi ve
    benzersiz fantastik isimler içeren hazır bir üye kadrosu üretir.
    """
    theme_key = _get_theme_key(faction_type)
    theme = THEMES[theme_key]
    roles = theme["roles"]
    prefixes = theme["prefixes"]

    # Rastgele benzersiz isimler ve lakaplar seçiyoruz
    selected_names = random.sample(FIRST_NAMES, min(count, len(FIRST_NAMES)))
    selected_prefixes = random.sample(prefixes, min(count, len(prefixes)))

    roster = []
    for i in range(count):
        first = selected_names[i]
        prefix = selected_prefixes[i]
        role = roles[i] if i < len(roles) else "Lonca Üyesi"

        # 2 farklı isim kombinasyon stili:
        # 1. "Gölge Jax" veya 2. "Corin 'Sessizadım'"
        if random.random() > 0.4:
            full_name = f"{prefix} {first}"
        else:
            full_name = f"{first} '{prefix}'"

        roster.append({
            "name": full_name,
            "role": role
        })

    return roster