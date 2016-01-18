from django.db import models
from djangotoolbox.fields import EmbeddedModelField

# Create your models here.
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


'''
from searchapp import models
loadup_info = [\
	("http://purl.obolibrary.org/obo/NCBITaxon_3262","Dutch rush"),\
	("http://purl.obolibrary.org/obo/CHEBI_27789","Dutch liquid"),\
	("http://purl.obolibrary.org/obo/NCBITaxon_158174","Dutch grass"),\
	("http://purl.obolibrary.org/obo/NCBITaxon_267265","Dutch eggplant"),\
	("http://www.orpha.net/ORDO/Orphanet_100006","Hereditary cerebral hemorrhage with amyloidosis, Dutch type"),\
	("http://purl.obolibrary.org/obo/GEO_000000229","Sint Maarten (Dutch part)"),\
	("http://purl.obolibrary.org/obo/NCBITaxon_283010","Phytophthora hybrid Dutch variant"),\
	("http://purl.obolibrary.org/obo/NCBITaxon_35876","Dutch iris")]
for tupl in loadup_info:
	models.Annotation(\
		triple=models.Triple(\
			subject=models.TripleElement(iri="https://b2share.eudat.eu/record/30",label="Orthography-based dating and localisation of Middle Dutch charters", definition="",curation_status="", ontology_iri="",ontology_shortname="",ontology_version="",),\
			predicate=models.TripleElement(iri="http://purl.obolibrary.org/obo/IAO_0000136",label="is about",definition="Is_about is a (currently) primitive relation that relates an information artifact to an entity.",curation_status="pending final vetting",ontology_iri="http://purl.obolibrary.org/obo/iao.owl",ontology_shortname="IAO",ontology_version="2015,02,23",),\
			object=models.TripleElement(\
				iri=tupl[0],\
				label=tupl[1],
				definition="",
				curation_status="",
				ontology_iri="",
				ontology_shortname="",\
				ontology_version="",\
			),\
		),\
		provenance=models.Provenance(\
		  createdBy="abremaud@esciencefactory.com",
		),\
	).save()

'''
#models.Annotation(\
    # triple=models.Triple(\
    #   subject=models.TripleElement(iri='https://b2share.eudat.eu/record/30'), \
    # predicate=models.TripleElement(iri='http://purl.obolibrary.org/obo/IAO_0000136', \
    # label='is about', \
    # definition='Is_about is a (currently) primitive relation that relates an information artifact to an entity.', \
    # curation_status='pending final vetting', \
    # ontology_iri='http://purl.obolibrary.org/obo/iao.owl', \
    # ontology_shortname='IAO', ontology_version = '2015,02,23'), \
    # object=models.TripleElement(iri='http://purl.obolibrary.org/obo/NCBITaxon_3262',label='Dutch rush')), provenance=models.Provenance( createdBy = 'abremaud@esciencecfactory.com' )).save()