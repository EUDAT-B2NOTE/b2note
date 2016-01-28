from django.db import models
from djangotoolbox.fields import EmbeddedModelField

class TripleElement(models.Model):
	iri 			= models.CharField( max_length = 4096 )
	label 			= models.CharField( max_length = 1024, blank = True )
	definition		= models.TextField( blank = True )
	curation_status		= models.CharField( max_length = 16, blank = True )
	ontology_iri 		= models.CharField( max_length = 4096, blank = True )
	ontology_shortname 	= models.CharField( max_length = 16, blank = True )
	ontology_version	= models.CommaSeparatedIntegerField( max_length = 16, blank = True )



class Triple(models.Model):
	subject 	= EmbeddedModelField( 'TripleElement' )
	predicate 	= EmbeddedModelField( 'TripleElement' )
	object 		= EmbeddedModelField( 'TripleElement' )



class Provenance(models.Model):
	createdBy 	= models.CharField( max_length = 1024, blank = True )
	createdOn 	= models.DateTimeField( auto_now_add = True )
	modifiedOn 	= models.DateTimeField( auto_now = True )



class Annotation(models.Model):
	triple 		= EmbeddedModelField( 'Triple' )
	provenance 	= EmbeddedModelField( 'Provenance' )

