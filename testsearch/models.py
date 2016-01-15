from django.db import models

# Create your models here.
class DataTest(models.Model):
    ontoId = models.CharField(max_length=200)
    labels = models.CharField(max_length=2000)


