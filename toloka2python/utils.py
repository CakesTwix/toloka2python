"""Корисні функції, які можуть знадобляться програмісту"""

def convert_to_bytes(size):
    """Конвертує з рядка, наприклад 4.2GB у кількість байт"""
    multipliers = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}

    size = size.upper()
    number = float(size[:-2])
    unit = size[-2:]

    if unit not in multipliers:
        return 0

    return int(number * multipliers[unit])