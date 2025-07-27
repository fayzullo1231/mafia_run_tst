# models/game_state.py
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameState(Base):
    __tablename__ = "game_states"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, index=True)
    players = Column(JSON, default=[])
    assignments = Column(JSON, default={})
    phase = Column(String, default="day")
    day = Column(Integer, default=1)


# models/game_state.py

active_game = {
    "tentak_target": None,
    "is_active": False,
    "phase": "day",  # yoki 'night'
    "chat_id": None,
    "group_title": None,
    "message_id": None,
    "players": [],  # List[{"id":int,"name":str}]
    "assignments": {},  # user_id: role
    "healed_players": [],
    "sotuvchi_protected": [],
    "killed_by_mafia": None,
    "day": 1
}

# Rollar to‘plami
ROLE_POOL = [
    "don", "mafiya", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi",
    "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior",
    "mergan", "muxlis", "buqalamun", "ogri"
]

# Rollar nomlari
ROLE_NAMES_UZ = {
    "don": "🤵🏻 Don",
    "mafiya": "🤵🏼 Mafiya",
    "advokat": "👨🏼‍💼 Advokat",
    "kimyogar": "👨‍🔬 Kimyogar",
    "donning_xotini": "🤵🏻‍♀️ Donning xotini",
    "komissar": "🕵🏻‍♂ Komissar",
    "shifokor": "👨🏼‍⚕️ Shifokor",
    "daydi": "🧙🏼‍♂️ Daydi",
    "serjant": "👮🏻‍♂ Serjant",
    "kamikadze": "💣 Kamikadze",
    "mashuqa": "💃 Mashuqa",
    "oqituvchi": "👩🏻‍🏫 O‘qituvchi",
    "suidsid": "🧌 Suidsid",
    "tentak": "👨🏻‍🦲 Tentak",
    "sotuvchi": "🎁 Sotuvchi",
    "afirist": "🤹🏻‍♂ Afirist",
    "majnun": "🕺🏻 Majnun",
    "manyak": "🔪 Manyak",
    "minior": "☠️ Minior",
    "mergan": "👨🏻‍🎤 Mergan",
    "muxlis": "🔮 Muxlis",
    "buqalamun": "🦎 Buqalamun",
    "ogri": "🥷🏻 O‘g‘ri",
    "tinch": "👨🏼 Tinch aholi"
}

# Rollar soniga qarab tanlash

def get_roles_for_player_count(count: int) -> list[str]:
    if count == 5:
        return ["don", "komissar", "shifokor", "kamikadze", "serjant"]
    elif count == 6:
        return ["don", "mafiya", "komissar", "shifokor", "daydi", "manyak"]
    elif count == 7:
        return ["don", "mafiya", "komissar", "shifokor", "daydi", "manyak", "buqalamun"]
    elif count == 8:
        return ["don", "mafiya", "mafiya", "komissar", "shifokor", "daydi", "manyak", "buqalamun"]
    elif count == 9:
        return ["don", "mafiya", "mafiya", "advokat", "komissar", "shifokor", "daydi", "manyak", "buqalamun"]
    elif count == 10:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "komissar", "shifokor", "daydi", "manyak", "buqalamun"]
    elif count == 11:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "manyak", "buqalamun"]
    elif count == 12:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "manyak", "buqalamun"]
    elif count == 13:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "manyak", "buqalamun"]
    elif count == 14:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "manyak", "buqalamun"]
    elif count == 15:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "manyak", "buqalamun"]
    elif count == 16:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "manyak", "buqalamun"]
    elif count == 17:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "manyak"]
    elif count == 18:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "manyak"]
    elif count == 19:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak"]
    elif count == 20:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior"]
    elif count == 21:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan"]
    elif count == 22:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan", "muxlis"]
    elif count == 23:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan", "muxlis", "buqalamun"]
    elif count == 24:
        return ["don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini", "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan", "muxlis", "buqalamun", "ogri"]
    else:
        raise ValueError("Kamida 5 ta o‘yinchi kerak.")
