from models.game_state import active_game

def get_commissioner_check_result(target_id: int) -> str:
    """
    Komissar odamni tekshirganida,
    - agar o‘zi advokat bo‘lsa → uni doim tinch deb ko‘rsatadi
    - agar tekshirilayotgan odam mafiya/don bo‘lsa va advokat o‘yinda bo‘lsa → uni ham tinch deb ko‘rsatadi
    """
    role = active_game["assignments"].get(target_id, "nomaʼlum")

    # Agar o‘zi advokat bo‘lsa → uni har doim tinch deb ko‘rsatish
    if role == "advokat":
        return "tinch"

    # Agar mafiya yoki don bo‘lsa va advokat o‘yinda bo‘lsa → tinch deb ko‘rsatiladi
    if role in ["mafiya", "don"]:
        if "advokat" in active_game["assignments"].values():
            return "tinch"

    # Aks holda haqiqiy rolini qaytarish
    return role
