import datetime
import time
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from rest_framework.views import APIView
from api_audit.models import APIRequestLog


def get_client_ip(request):
    """
    Extract client IP address from headers.
    Handles common reverse proxy headers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class DRFRequestLoggerMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        request._start_time = time.time()

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        view_class = getattr(view_func, 'cls', None)
        request._is_drf_view = bool(view_class and issubclass(view_class, APIView))

    @staticmethod
    def process_response(request, response):
        if not getattr(request, '_is_drf_view', False):
            return response

        # Timing
        duration_seconds = time.time() - getattr(request, '_start_time', time.time())
        duration = datetime.timedelta(seconds=duration_seconds)
        # User
        user = request.user if request.user.is_authenticated else None

        # Request metadata
        method = request.method
        path = request.get_full_path()
        status_code = response.status_code
        timestamp = now()
        remote_ip = get_client_ip(request)

        # Query params
        query_params = dict(request.GET)

        # Request body — scrubbed
        request_data = None
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                data = request.data.copy()
                for key in ['password', 'token', 'access', 'refresh']:
                    data.pop(key, None)
                request_data = data
            except Exception as e:
                request_data = {"error": "unreadable"}

        # Save to DB
        try:
            APIRequestLog.objects.create(
                user=user,
                method=method,
                path=path,
                status_code=status_code,
                duration=duration,
                timestamp=timestamp,
                query_params=query_params,
                request_data=request_data,
                remote_ip=remote_ip,
            )
        except Exception as e:
            pass

        return response
