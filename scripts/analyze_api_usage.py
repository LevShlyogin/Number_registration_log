import re
from collections import Counter
from pathlib import Path

# Паттерн для парсинга нашего нового формата логов
LOG_PATTERN = re.compile(r"API_CALL method=(\S+) path=(\S+) status_code=(\d+)")

def analyze_logs(log_file: Path):
    """Анализирует лог-файл и выводит статистику по эндпоинтам."""
    if not log_file.exists():
        print(f"Ошибка: Файл логов '{log_file}' не найден.")
        return None

    usage_counter = Counter()
    
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = LOG_PATTERN.search(line)
            if not match:
                continue

            method, path, status_code_str = match.groups()
            
            # Считаем только успешные запросы (статус 2xx)
            if status_code_str.startswith("2"):
                usage_counter[(method, path)] += 1

    print("--- Статистика использования API (успешные вызовы) ---")
    if not usage_counter:
        print("Нет данных об успешных вызовах.")
        return

    for (method, path), count in usage_counter.most_common():
        print(f"{count:<10} {method:<8} {path}")
        
    return set(usage_counter.keys())

if __name__ == "__main__":
    analyze_logs(Path("api_usage.log"))