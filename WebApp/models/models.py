from django.db import models

class PredictionData(models.Model):
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=6)
    age = models.IntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    prediction_result = models.CharField(max_length=100)