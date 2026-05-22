import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from predictions.models import Prediction


@login_required
def home(request):
    qs = Prediction.objects.filter(user=request.user)
    pred_counts = dict(
        qs.values('prediction_type')
        .annotate(c=Count('id'))
        .values_list('prediction_type', 'c')
    )
    recent_preds = qs.order_by('-created_at')[:8]

    today = date.today()
    daily = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        cnt = qs.filter(created_at__date=d).count()
        daily.append({'date': d.strftime('%a'), 'count': cnt})

    return render(request, 'dashboard/home.html', {
        'pred_counts': json.dumps(pred_counts),
        'pred_counts_py': pred_counts,
        'daily_chart': json.dumps(daily),
        'recent_preds': recent_preds,
        'total_preds': sum(pred_counts.values()),
    })
