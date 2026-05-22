"""User-scoped health dashboard data (never crosses users)."""
from django.db.models import Count

from .models import PredictionHistory

PREDICTION_LABELS = dict(PredictionHistory.PREDICTION_TYPES)


def get_user_health_dashboard(user):
    """Build stats and history for one user only."""
    history = PredictionHistory.objects.filter(user=user).order_by('-created_at')
    by_type = (
        history.values('prediction_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    type_stats = [
        {
            'type': row['prediction_type'],
            'label': PREDICTION_LABELS.get(row['prediction_type'], row['prediction_type']),
            'count': row['count'],
        }
        for row in by_type
    ]

    bmi_records = [
        {
            'date': h.created_at.strftime('%b %d'),
            'bmi': h.result.get('bmi'),
            'category': h.result.get('category', ''),
        }
        for h in history.filter(prediction_type='bmi')[:12]
    ]
    bmi_records.reverse()

    recent = history[:15]

    return {
        'total_predictions': history.count(),
        'type_stats': type_stats,
        'bmi_trend': bmi_records,
        'recent_predictions': recent,
        'last_prediction': history.first(),
    }
