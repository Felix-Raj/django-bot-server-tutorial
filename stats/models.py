from django.db import models


class BotUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=200, default='', null=True)


class BotHit(models.Model):
    user = models.ForeignKey(to=BotUser, on_delete=models.CASCADE)
    button = models.CharField(max_length=200)
    count = models.IntegerField(default=0)
