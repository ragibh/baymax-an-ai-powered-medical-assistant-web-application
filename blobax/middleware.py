"""
Project middleware — login protection for app routes.
"""
from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class LoginRequiredMiddleware:
    """
    Redirect anonymous users to login before dashboard, predictions, or emergency apps.
    Public: home, users (login/register), admin, static, media.
    """

    PUBLIC_PREFIXES = (
        '/users/login',
        '/users/register',
        '/users/logout',
        '/accounts/',
        '/contact/',
        '/admin/',
        '/static/',
        '/media/',
    )

    PROTECTED_PREFIXES = (
        '/dashboard/',
        '/predictions/',
        '/emergency/',
        '/users/profile',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if path == '/' or any(path.startswith(p) for p in self.PUBLIC_PREFIXES):
            return self.get_response(request)

        if request.user.is_authenticated:
            return self.get_response(request)

        if any(path.startswith(p) for p in self.PROTECTED_PREFIXES):
            return redirect_to_login(
                request.get_full_path(),
                login_url=settings.LOGIN_URL,
            )

        return self.get_response(request)
