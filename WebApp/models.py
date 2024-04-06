from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class PredictionData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=6)
    age = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    prediction_result = models.CharField(max_length=100)
    submitted_time = models.DateTimeField(default=timezone.now)
