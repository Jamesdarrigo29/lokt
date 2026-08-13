import uuid

from starlette.middleware.base import BaseHTTPMiddleware

WORKSPACE_COOKIE = "workspace_id"
WORKSPACE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year


class WorkspaceMiddleware(BaseHTTPMiddleware):
    """Assigns every visitor an anonymous workspace via an httpOnly cookie, so
    one visitor's ingested policies/chats aren't visible to another. Not a
    login system — see rag-design.md for the tradeoffs of this approach.
    """

    async def dispatch(self, request, call_next):
        workspace_id = request.cookies.get(WORKSPACE_COOKIE)
        is_new = False

        if not workspace_id:
            workspace_id = str(uuid.uuid4())
            is_new = True

        request.state.workspace_id = workspace_id

        response = await call_next(request)

        if is_new:
            response.set_cookie(
                WORKSPACE_COOKIE,
                workspace_id,
                max_age=WORKSPACE_COOKIE_MAX_AGE,
                httponly=True,
                secure=True,
                samesite="none",
            )

        return response
