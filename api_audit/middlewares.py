import datetime
import time
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from api_audit.models import APIRequestLog
from rest_framework.views import APIView


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class DRFRequestLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_class = getattr(view_func, 'cls', None)
        request._is_drf_view = bool(view_class and issubclass(view_class, APIView))

    def process_exception(self, request, exception):
        if not getattr(request, '_is_drf_view', False):
            return None

        try:
            duration = datetime.timedelta(seconds=time.time() - getattr(request, '_start_time', time.time()))
            method = request.method
            path = request.get_full_path()
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            remote_ip = get_client_ip(request)
            query_params = dict(request.GET)

            request_data = None
            if method in ['POST', 'PUT', 'PATCH']:
                try:
                    data = request.data.copy()
                    for key in ['password', 'token', 'access', 'refresh']:
                        data.pop(key, None)
                    request_data = data
                except Exception:
                    request_data = {"error": "unreadable"}

            trace = traceback.format_exc()

            APIRequestLog.objects.create(
                user=user,
                method=method,
                path=path,
                status_code=500,  # Cannot get exact DRF response status here
                duration=duration,
                timestamp=now(),
                query_params=query_params,
                request_data=request_data,
                remote_ip=remote_ip,
                error_trace=trace,
            )
        except Exception:
            pass

        return None  # Continue exception handling as normal

    def process_response(self, request, response):
        if not getattr(request, '_is_drf_view', False):
            return response

        # Avoid double-logging for errors
        if response.status_code >= 500:
            return response

        try:
            duration = datetime.timedelta(seconds=time.time() - getattr(request, '_start_time', time.time()))
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            method = request.method
            path = request.get_full_path()
            remote_ip = get_client_ip(request)
            query_params = dict(request.GET)

            request_data = None
            if method in ['POST', 'PUT', 'PATCH']:
                try:
                    data = request.data.copy()
                    for key in ['password', 'token', 'access', 'refresh']:
                        data.pop(key, None)
                    request_data = data
                except Exception:
                    request_data = {"error": "unreadable"}

            APIRequestLog.objects.create(
                user=user,
                method=method,
                path=path,
                status_code=response.status_code,
                duration=duration,
                timestamp=now(),
                query_params=query_params,
                request_data=request_data,
                remote_ip=remote_ip,
                error_trace=None,
            )
        except Exception:
            pass

        return response
