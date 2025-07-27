from models.game_state import active_game

def apply_majnun_redirect(original_targets: dict) -> dict:
    """
    Majnun rolining Layliga ergashish logikasini qo‘llaydi.
    original_targets — har bir roldagi tanlangan odamlar (masalan: {"mafiya_target": user_id, "doctor_target": user_id, ...})
    """

    majnun_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "majnun"),
        None
    )

    layli_id = active_game.get("majnun_layli")

    if not majnun_id or not layli_id:
        return original_targets  # hech qanday o‘zgarish yo‘q

    # Rollar nomlarini topamiz
    role_map = {v: k for k, v in active_game["assignments"].items()}

    # Har bir rolda tanlangan odamni topamiz va Laylining o‘rniga Majnunni o‘tkazamiz
    updated_targets = original_targets.copy()

    for role_key in ["doctor_target", "commissioner_check", "serjant_target", "daydi_target", "tentak_target"]:
        if original_targets.get(role_key) == layli_id:
            updated_targets[role_key] = majnun_id

    return updated_targets
