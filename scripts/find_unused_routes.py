from fastapi.routing import APIRoute
from app.main import app # Импортируем ваше FastAPI приложение
from scripts.analyze_api_usage import analyze_logs
from pathlib import Path

def get_all_routes():
    """Возвращает множество всех определенных в приложении маршрутов в формате (METHOD, /full/path)."""
    routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path not in ["/redoc", "/openapi.json", "/docs"]:
             for method in route.methods:
                 routes.add((method, route.path))
    return routes

if __name__ == "__main__":
    all_defined_routes = get_all_routes()
    used_routes = analyze_logs(Path("api_usage.log"))
    
    if used_routes is None:
        exit(1)

    unused_routes = all_defined_routes - used_routes
    
    print("\n\n--- 💀 Кандидаты на удаление (не использовались ни разу) ---")
    if not unused_routes:
        print("Все эндпоинты использовались. Отличная работа!")
    else:
        for method, path in sorted(list(unused_routes)):
            print(f"{method:<8} {path}")