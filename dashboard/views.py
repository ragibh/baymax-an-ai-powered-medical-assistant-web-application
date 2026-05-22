from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from predictions.utils import get_user_health_dashboard


@login_required
def home(request):
    """Post-login hub — user-scoped health summary only."""
    health = get_user_health_dashboard(request.user)
    return render(request, 'dashboard/home.html', {'health': health})