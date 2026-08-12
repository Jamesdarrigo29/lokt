from slowapi import Limiter
from slowapi.util import get_remote_address

from workspace import WORKSPACE_COOKIE


def _workspace_key(request) -> str:
    return request.cookies.get(WORKSPACE_COOKIE) or get_remote_address(request)


limiter = Limiter(key_func=_workspace_key)
