from django.conf.urls import url

from stats.views import BotHitStats

app_name = 'stats'
urlpatterns = [
    url('$', BotHitStats.as_view(), name='show_stats'),
]