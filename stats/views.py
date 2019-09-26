from django.views.generic import ListView

from stats.models import BotHit


class BotHitStats(ListView):
    model = BotHit
