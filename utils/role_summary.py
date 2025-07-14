from models.game_state import ROLE_NAMES_UZ, active_game

# Rol kategoriyalari
TANCH_AHOLILAR = {"tinch", "serjant", "oqituvchi", "daydi", "kamikadze", "komissar", "shifokor"}
MAFIYALAR = {"don", "mafiya", "advokat"}
BETARAF_ROLLAR = {"mashuqa", "oqituvchi", "afirist", "sotuvchi", "tentak", "muxlis"}
YAKKA_ROLLAR = {"minior", "suidsid", "manyak", "mergan", "ogri", "buqalamun", "kimyogar", "donning_xotini", "majnun"}

# Rol bo‘yicha ajratamiz
category_map = {
    "🔵 Tinch axolilar": [],
    "🔴 Mafiyalar": [],
    "🔴 Advokat": [],
    "🟡 Betaraflar": [],
    "⚫ Yakka rollar": [],
}


def generate_role_summary(assignments: dict) -> str:
    players = active_game["players"]
    text = "<b>Tirik o'yinchilar:</b>\n"

    for i, player in enumerate(players, start=1):
        text += f"{i}. <a href='tg://user?id={player['id']}'>{player['name']}</a>\n"


    for user_id, role in assignments.items():
        if role in TANCH_AHOLILAR:
            category_map["🔵 Tinch axolilar"].append(role)
        elif role in MAFIYALAR:
            category_map["🔴 Mafiyalar"].append(role)
        elif role in BETARAF_ROLLAR:
            category_map["🟡 Betaraflar"].append(role)
        elif role in YAKKA_ROLLAR:
            category_map["⚫ Yakka rollar"].append(role)

    text += "\n<b>Ulardan:</b>\n"

    for cat_name, roles in category_map.items():
        if not roles:
            continue
        unique_roles = set(roles)
        role_counts = []
        for role in unique_roles:
            count = roles.count(role)
            name = ROLE_NAMES_UZ.get(role, role)
            role_counts.append(f"{name}" if count == 1 else f"{name} x{count}")
        joined = ", ".join(role_counts)
        text += f"\n{cat_name} – {len(roles)}\n{joined}\n"

    text += f"\n<b>Jami:</b> {len(assignments)} ta"
    return text

