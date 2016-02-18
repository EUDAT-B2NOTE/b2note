from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager



class Annotation(models.Model):
    jsonld_id   = models.CharField( max_length = 4096, null = True )
    jsonld_type = models.CharField( max_length = 256 )
    body        = models.CharField( max_length = 4096, null = True )
    target      = models.CharField( max_length = 4096 )
    # http://stackoverflow.com/questions/23546480/no-raw-query-method-in-my-django-object
    #objects     = MongoDBManager()
