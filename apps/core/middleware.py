import logging
import time

logger = logging.getLogger("apps.request")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return response
        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.get_full_path(),
            response.status_code,
            elapsed_ms,
        )
        return response
