def second_readable(seconds: int) -> str:
    """Преобразует секунды в читаемый формат"""
    if seconds == 0:
        return "0 секунд"
    
    # Единицы времени и их значения в секундах
    time_units = [
        ('год', 365 * 24 * 3600),
        ('месяц', 30 * 24 * 3600),
        ('неделя', 7 * 24 * 3600),
        ('день', 24 * 3600),
        ('час', 3600),
        ('минута', 60),
        ('секунда', 1)
    ]
    
    parts = []
    remaining = seconds
    
    for unit_name, unit_seconds in time_units:
        if remaining >= unit_seconds:
            count = int(remaining // unit_seconds)
            remaining %= unit_seconds
            
            if count == 1:
                parts.append(f"{count} {unit_name}")
            elif 2 <= count <= 4:
                parts.append(f"{count} {unit_name}а" if unit_name in ['год', 'день'] else f"{count} {unit_name}ы")
            else:
                parts.append(f"{count} {unit_name}ов" if unit_name in ['год', 'день'] else f"{count} {unit_name}")
    
    return ", ".join(parts) if parts else "менее секунды"

def find_first_key(obj, key):
    """Рекурсивно ищет первое значение для указанного ключа"""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                result = find_first_key(v, key)
                if result is not None:
                    return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_first_key(item, key)
            if result is not None:
                return result
    return None