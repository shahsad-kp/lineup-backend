from django.db.models import IntegerChoices, TextChoices


class StatusCode(IntegerChoices):
    # 2xx
    OK = 200, "200 OK"
    CREATED = 201, "201 Created"
    ACCEPTED = 202, "202 Accepted"
    NO_CONTENT = 204, "204 No Content"

    # 3xx
    MOVED_PERMANENTLY = 301, "301 Moved Permanently"
    FOUND = 302, "302 Found"
    NOT_MODIFIED = 304, "304 Not Modified"

    # 4xx
    BAD_REQUEST = 400, "400 Bad Request"
    UNAUTHORIZED = 401, "401 Unauthorized"
    FORBIDDEN = 403, "403 Forbidden"
    NOT_FOUND = 404, "404 Not Found"
    METHOD_NOT_ALLOWED = 405, "405 Method Not Allowed"
    CONFLICT = 409, "409 Conflict"
    GONE = 410, "410 Gone"
    UNSUPPORTED_MEDIA_TYPE = 415, "415 Unsupported Media Type"
    UNPROCESSABLE_ENTITY = 422, "422 Unprocessable Entity"
    TOO_MANY_REQUESTS = 429, "429 Too Many Requests"

    # 5xx
    SERVER_ERROR = 500, "500 Internal Server Error"
    BAD_GATEWAY = 502, "502 Bad Gateway"
    SERVICE_UNAVAILABLE = 503, "503 Service Unavailable"
    GATEWAY_TIMEOUT = 504, "504 Gateway Timeout"


class HTTPMethod(TextChoices):
    GET = 'GET', 'GET'
    POST = 'POST', 'POST'
    PUT = 'PUT', 'PUT'
    PATCH = 'PATCH', 'PATCH'
    DELETE = 'DELETE', 'DELETE'
    OPTIONS = 'OPTIONS', 'OPTIONS'
    HEAD = 'HEAD', 'HEAD'
