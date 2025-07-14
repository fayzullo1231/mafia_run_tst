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
    "is_active": False,
    "phase": "day",  # yoki 'night'
    "chat_id": None,
    "group_title": None,
    "message_id": None,
    "players": [],  # List[{"id":int,"name":str}]
    "assignments": {},  # user_id: role
    "healed_players": [],
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
roles_for_5 = [
    "don",        # Mafiya
    "komissar",   # Tinch aholi
    "shifokor",   # Tinch aholi
    "daydi",      # Tinch aholi
    "manyak"
]

roles_for_6 = [
    "don", "mafiya", "komissar", "shifokor", "daydi", "manyak"
]

roles_for_7 = [
    "don", "mafiya", "komissar", "shifokor", "daydi", "manyak", "buqalamun"
]

roles_for_8 = [
    "don", "mafiya", "mafiya", "komissar", "shifokor", "daydi", "manyak", "buqalamun"
]

roles_for_9 = [
    "don", "mafiya", "mafiya", "advokat", "komissar", "shifokor", "daydi", "manyak", "buqalamun"
]

roles_for_10 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "komissar", "shifokor", "daydi", "manyak", "buqalamun"
]

roles_for_11 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "manyak", "buqalamun"
]

roles_for_12 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "manyak", "buqalamun"
]

roles_for_13 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "manyak", "buqalamun"
]

roles_for_14 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "manyak", "buqalamun"
]

roles_for_15 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "manyak", "buqalamun"
]

roles_for_16 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa", "oqituvchi", "suidsid", "manyak", "buqalamun"
]

roles_for_17 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "manyak"
]

roles_for_18 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "manyak"
]

roles_for_19 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak"
]

roles_for_20 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior"
]

roles_for_21 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan"
]

roles_for_22 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan", "muxlis"
]

roles_for_23 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun", "manyak", "minior", "mergan", "muxlis", "buqalamun"
]

roles_for_24 = [
    "don", "mafiya", "mafiya", "advokat", "kimyogar", "donning_xotini",
    "komissar", "shifokor", "daydi", "serjant", "kamikadze", "mashuqa",
    "oqituvchi", "suidsid", "tentak", "sotuvchi", "afirist", "majnun",
    "manyak", "minior", "mergan", "muxlis", "buqalamun", "ogri"
]
