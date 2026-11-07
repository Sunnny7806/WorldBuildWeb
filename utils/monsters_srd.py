import json

SRD_MONSTERS = [
    {
        "name": "Goblin",
        "cr": "1/4",
        "monster_type": "İnsansı (Goblinoid)",
        "size": "Küçük",
        "armor_class": 15,
        "hp_max": 7,
        "speed": "30 ft",
        "stats": {"STR": 8, "DEX": 14, "CON": 10, "INT": 10, "WIS": 8, "CHA": 8},
        "actions": [
            {"name": "Pala (Scimitar)", "bonus": "+4", "damage": "1d6+2 Kesici", "desc": "Yakın dövüş silah saldırısı, menzil 5 ft."},
            {"name": "Kısa Yay (Shortbow)", "bonus": "+4", "damage": "1d6+2 Delici", "desc": "Menzilli silah saldırısı, menzil 80/320 ft."}
        ],
        "traits": "Çevik Kaçış: Goblin her tur bonus eylem olarak Ayrıl (Disengage) veya Saklan (Hide) aksiyonu alabilir."
    },
    {
        "name": "Kurt (Wolf)",
        "cr": "1/4",
        "monster_type": "Canavar",
        "size": "Orta",
        "armor_class": 13,
        "hp_max": 11,
        "speed": "40 ft",
        "stats": {"STR": 12, "DEX": 15, "CON": 12, "INT": 3, "WIS": 12, "CHA": 6},
        "actions": [
            {"name": "Isırık (Bite)", "bonus": "+4", "damage": "2d4+2 Delici", "desc": "Hedef DC 11 Güç kurtarma zarını geçemezse yere düşer (Prone)."}
        ],
        "traits": "Sürü Taktikleri: Kurdun saldırdığı hedefin 5 ft yakınında bilinci açık bir müttefiki varsa saldırı zarında avantaja sahiptir."
    },
    {
        "name": "İskelet (Skeleton)",
        "cr": "1/4",
        "monster_type": "Hortlak (Undead)",
        "size": "Orta",
        "armor_class": 13,
        "hp_max": 13,
        "speed": "30 ft",
        "stats": {"STR": 10, "DEX": 14, "CON": 15, "INT": 6, "WIS": 8, "CHA": 5},
        "actions": [
            {"name": "Kısa Kılıç (Shortsword)", "bonus": "+4", "damage": "1d6+2 Delici", "desc": "Yakın dövüş silah saldırısı."},
            {"name": "Kısa Yay (Shortbow)", "bonus": "+4", "damage": "1d6+2 Delici", "desc": "Menzilli saldırı, menzil 80/320 ft."}
        ],
        "traits": "Ezici hasara karşı zafiyeti vardır. Zehir hasarına ve zehirlenme durumuna bağışıktır."
    },
    {
        "name": "Zombi (Zombie)",
        "cr": "1/4",
        "monster_type": "Hortlak (Undead)",
        "size": "Orta",
        "armor_class": 8,
        "hp_max": 22,
        "speed": "20 ft",
        "stats": {"STR": 13, "DEX": 6, "CON": 16, "INT": 3, "WIS": 6, "CHA": 5},
        "actions": [
            {"name": "Ezici Vuruş (Slam)", "bonus": "+3", "damage": "1d6+1 Ezici", "desc": "Yakın dövüş saldırısı."}
        ],
        "traits": "Hortlak Dayanıklılığı: Canı 0'a düşüren hasar kutsal veya kritik değilse, DC 5 + hasar kadar CON kurtarma zarı atar; geçerse 1 HP ile hayatta kalır."
    },
    {
        "name": "Haydut (Bandit)",
        "cr": "1/8",
        "monster_type": "İnsansı",
        "size": "Orta",
        "armor_class": 12,
        "hp_max": 11,
        "speed": "30 ft",
        "stats": {"STR": 11, "DEX": 12, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
        "actions": [
            {"name": "Pala (Scimitar)", "bonus": "+3", "damage": "1d6+1 Kesici", "desc": "Yakın dövüş saldırısı."},
            {"name": "Tatar Yayı (Light Crossbow)", "bonus": "+3", "damage": "1d8 Delici", "desc": "Menzil 80/320 ft."}
        ],
        "traits": "Organize Çete: Tehditkar ve kurnaz paralı haydut."
    },
    {
        "name": "Ogre",
        "cr": "2",
        "monster_type": "Dev",
        "size": "Büyük",
        "armor_class": 11,
        "hp_max": 59,
        "speed": "40 ft",
        "stats": {"STR": 19, "DEX": 8, "CON": 16, "INT": 5, "WIS": 7, "CHA": 7},
        "actions": [
            {"name": "Büyük Sopa (Greatclub)", "bonus": "+6", "damage": "2d8+4 Ezici", "desc": "Yakın dövüş saldırısı, erişim 5 ft."},
            {"name": "Cirit (Javelin)", "bonus": "+6", "damage": "2d6+4 Delici", "desc": "Fırlatma menzili 30/120 ft."}
        ],
        "traits": "Vahşi Güç: Büyük ve kaba kuvvet uygulayan dev."
    },
    {
        "name": "Karasöl (Gelatinous Cube)",
        "cr": "2",
        "monster_type": "Balçık (Ooze)",
        "size": "Büyük",
        "armor_class": 6,
        "hp_max": 84,
        "speed": "15 ft",
        "stats": {"STR": 14, "DEX": 3, "CON": 20, "INT": 1, "WIS": 6, "CHA": 1},
        "actions": [
            {"name": "Sahte Kol (Pseudopod)", "bonus": "+4", "damage": "3d6 Asit", "desc": "Yakın dövüş saldırısı."},
            {"name": "Yutma (Engulf)", "bonus": "DC 12 DEX", "damage": "6d6 Asit", "desc": "Kendi alanındaki hedefleri içine çeker ve asitle sindirir."}
        ],
        "traits": "Saydam Gövde: Fark edilmesi için DC 15 Algı kontrolü gerekir. Körleşme, sağırlık ve sersemlemeye bağışıktır."
    },
    {
        "name": "Kült Fanatiği (Cult Fanatic)",
        "cr": "2",
        "monster_type": "İnsansı",
        "size": "Orta",
        "armor_class": 13,
        "hp_max": 33,
        "speed": "30 ft",
        "stats": {"STR": 11, "DEX": 14, "CON": 12, "INT": 10, "WIS": 13, "CHA": 14},
        "actions": [
            {"name": "Çoklu Saldırı", "bonus": "2x", "damage": "Hançer", "desc": "Tur başına iki hançer saldırısı yapar."},
            {"name": "Hançer (Dagger)", "bonus": "+4", "damage": "1d4+2 Delici", "desc": "Yakın veya fırlatmalı saldırı."}
        ],
        "traits": "Büyü Yeteneği: 4. seviye büyücü (Kutsal Alev, Kalkan Felsefesi, Ruh Muhafızları)."
    },
    {
        "name": "Genç Kırmızı Ejderha (Young Red Dragon)",
        "cr": "10",
        "monster_type": "Ejderha",
        "size": "Büyük",
        "armor_class": 18,
        "hp_max": 178,
        "speed": "40 ft, Uçma 80 ft",
        "stats": {"STR": 23, "DEX": 10, "CON": 21, "INT": 14, "WIS": 11, "CHA": 19},
        "actions": [
            {"name": "Çoklu Saldırı", "bonus": "3x", "damage": "1 Isırık, 2 Pençe", "desc": "Bir ısırık ve iki pençe saldırısı yapar."},
            {"name": "Isırık (Bite)", "bonus": "+10", "damage": "2d10+6 Delici + 1d6 Ateş", "desc": "Erişim 10 ft."},
            {"name": "Pençe (Claw)", "bonus": "+10", "damage": "2d6+6 Kesici", "desc": "Erişim 5 ft."},
            {"name": "Ateş Nefesi (Fire Breath)", "bonus": "DC 17 DEX", "damage": "16d6 Ateş", "desc": "30 ft koni alanı (Recharge 5-6)."}
        ],
        "traits": "Ateş Bağışıklığı: Ateş hasarından etkilenmez. Körgörüş 30 ft, Karanlık Görüşü 120 ft."
    }
]


def get_srd_monsters():
    """Tüm hazır SRD canavarlarını döner."""
    return SRD_MONSTERS
