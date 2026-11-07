import re
import random

def get_modifier(score: int) -> int:
    """D&D 5e stat puanından (örn: 14) bonus/ceza değerini (-5 ile +10 arası) hesaplar."""
    try:
        s = int(score)
        return (s - 10) // 2
    except (ValueError, TypeError):
        return 0

def format_modifier(score: int) -> str:
    """Puanın modifier'ını '+2' veya '-1' şeklinde string formatında döner."""
    mod = get_modifier(score)
    return f"+{mod}" if mod >= 0 else str(mod)

def roll_d20(bonus: int = 0) -> tuple[int, int]:
    """1d20 zarı atar. (doğal_zar, toplam) demetini döner."""
    natural = random.randint(1, 20)
    total = natural + bonus
    return natural, total

def roll_dice(expression: str) -> tuple[int, str]:
    """
    '2d6+3', '1d8', '3d4-1' veya düz sayı formatındaki ifadeleri çözer ve zar atar.
    Dönüş: (toplam_sonuç, açıklama_metni)
    Örn: (11, '2d6 (4, 4) + 3 = 11')
    """
    clean_expr = str(expression).strip().replace(" ", "").lower()
    
    # regex: (adet)d(zar_tipi)(opsiyonel +/- bonus)
    match = re.match(r'^(\d*)d(\d+)(?:([+-])(\d+))?$', clean_expr)
    if not match:
        # Eğer sadece düz bir sayıysa
        try:
            val = int(clean_expr)
            return val, str(val)
        except ValueError:
            return 0, "Geçersiz ifade"

    count_str, sides_str, sign, bonus_str = match.groups()
    count = int(count_str) if count_str else 1
    sides = int(sides_str)
    bonus = int(bonus_str) if bonus_str else 0
    if sign == "-":
        bonus = -bonus

    if count <= 0 or sides <= 0:
        return 0, "0"

    rolls = [random.randint(1, sides) for _ in range(count)]
    sum_rolls = sum(rolls)
    total = sum_rolls + bonus

    rolls_repr = ", ".join(map(str, rolls))
    if bonus > 0:
        breakdown = f"{count}d{sides} [{rolls_repr}] + {bonus} = {total}"
    elif bonus < 0:
        breakdown = f"{count}d{sides} [{rolls_repr}] - {abs(bonus)} = {total}"
    else:
        breakdown = f"{count}d{sides} [{rolls_repr}] = {total}"

    return total, breakdown
