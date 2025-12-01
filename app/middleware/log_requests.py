import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Создаем специальный логгер, чтобы его вывод можно было легко направить в отдельный файл
logger = logging.getLogger("api_usage")

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Логируем в структурированном формате для легкого парсинга
        logger.info(
            "API_CALL method=%s path=%s status_code=%d duration=%.4f",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )
        
        return response