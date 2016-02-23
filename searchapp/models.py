from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager

class Annotation(models.Model):
    jsonld_id   = models.CharField( max_length = 4096, null = True )
    jsonld_type = models.CharField( max_length = 256 )
    body        = models.CharField( max_length = 4096, null = True )
    target      = models.CharField( max_length = 4096 )
    #language 	= models.CharField( max_length = 256, null=True ) #dc:language, [rfc5646]
    #format		= models.CharField( max_length = 256, null=True ) #dc:format, [rfc6838]
    #creator 	= ListField( EmbeddedModelField("Agent"), null=True ) # dcterms:creator
    created 	= models.DateTimeField( auto_now_add=True, null=True ) # dcterms:created MUST xsd:dateTime SHOULD timezone.
    # http://stackoverflow.com/questions/23546480/no-raw-query-method-in-my-django-object
    #objects     = MongoDBManager()
