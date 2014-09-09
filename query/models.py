from django.db import models
import os

# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents')
    def extension(self):
        name, extension = os.path.splitext(self.docfile.name)
        return extension

class Ontologies(models.Model):
    name = models.CharField(max_length=50)
    endpoint = models.CharField(max_length=100)
    prefix = models.CharField(max_length=100)
    concept = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    api = models.CharField(max_length=20)

#class EnvThes():
#    endpoint = "http://vocabs.lter-europe.net/PoolParty/sparql/EnvThes"
#    prefix = "skos:<http://www.w3.org/2004/02/skos/core#>"
#    concept = "skos:Concept"
#    label = "skos:prefLabel"
#
#class BioOntology():
#    endpoint = "http://sparql.bioontology.org/sparql/"
#    prefix = "omv:<http://omv.ontoware.org/2005/05/ontology#>"
#    concept = "omv:Ontology" 
#    label = "omv:name"
#

