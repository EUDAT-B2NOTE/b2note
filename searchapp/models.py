from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager



class Agent(models.Model):
	jsonld_id 	    = models.CharField( max_length = 4096, null=True ) #"https://b2note.bsc.es/agent/" + mongo_uid
	PERSON          = 'Human agent'
	ORGANISATION    = 'Organization agent'
	SOFTWARE        = 'Software agent'
	AGENT_CHOICES = (
        (PERSON, 'foaf:Person'),
        (ORGANISATION, 'foaf:Organization'),
        (SOFTWARE, 'prov:SoftwareAgent'),
    )
	jsonld_type	= ListField( models.CharField( max_length = 32, choices=AGENT_CHOICES), null=True ) #"Person" foaf:Person, "Organization" foaf:Organization, "Software" prov:SoftwareAgent
	name		= models.CharField( max_length = 2048, null=True ) #foaf:name
	account	    = models.CharField( max_length = 2048, null=True ) #foaf:nick
	email		= ListField( models.CharField(max_length = 2048), null=True ) #foaf:mbox
	homepage	= ListField( models.CharField(max_length = 4096), null=True ) #foaf:homepage


class TextualBody(models.Model):
	jsonld_id 	= models.CharField( max_length = 4096, null=True ) #"https://b2note.bsc.es/textualbody/" + mongo_uid
	jsonld_type	= ListField( models.CharField( max_length = 64 ), null=True ) # rdf:type; oa:TextualBody
	text        = models.TextField() # oa:text
	language 	= ListField( models.CharField( max_length = 256 ), null=True )  # dc:language, [rfc5646]
	format		= ListField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]
	BOOKMARKING     = "bookmarking"
	CLASSIFYING     = "classifing"
	COMMENTING      = "commenting"
	DESCRIBING      = "describing"
	EDITING         = "editing"
	HIGHLIGHTING    = "highlighting"
	IDENTIFYING     = "identifying"
	LINKING         = "linking"
	MODERATING      = "moderating"
	QUESTIONING     = "questioning"
	REPLYING        = "replying"
	REVIEWING       = "reviewing"
	TAGGING         = "tagging"
	MOTIVATION_CHOICES = (
        (BOOKMARKING,   "oa:bookmarking"), #oa:bookmarking
        (CLASSIFYING,   "oa:classifying"), #oa:classifying
        (COMMENTING,    "oa:commenting"),  #oa:commenting
        (DESCRIBING,    "oa:describing"),  #oa:describing
        (EDITING,       "oa:editing"),     #oa:editing
        (HIGHLIGHTING,  "oa:highlighting"),    #oa:highlighting
        (IDENTIFYING,   "oa:identifying"), #oa:identifying
        (LINKING,       "oa:linking"),     #oa:linking
        (MODERATING,    "oa:moderating"),  #oa:moderating
        (QUESTIONING,   "oa:questioning"), #oa:questioning
        (REPLYING,      "oa:replying"),    #oa:replying
        (REVIEWING,     "oa:reviewing"),   #oa:reviewing
        (TAGGING,       "oa:tagging"),     #oa:tagging
    )
	role	= models.CharField( max_length = 256, choices=MOTIVATION_CHOICES, null=True )
	# oa:hasRole = oa:Motivation


class ExternalResource(models.Model):
	jsonld_id 	= models.CharField( max_length = 4096, null=True )
	DATASET = "dataset"
	IMAGE   = "image"
	VIDEO   = "video"
	SOUND   = "sound"
	TEXT    = "text"
	RESOURCE_TYPE_CHOICES = (
        (DATASET,   "dctypes:Dataset"),
        (IMAGE,     "dctypes:StillImage"),
        (VIDEO,     "dctypes:MovingImage"),
        (SOUND,     "dctypes:Sound"),
        (TEXT,      "dctypes:Text"),
    )
	jsonld_type	= ListField( models.CharField( max_length = 64, choices=RESOURCE_TYPE_CHOICES), null=True ) #rdf:class
	language 	= ListField( models.CharField( max_length = 256 ), null=True )  # dc:language, [rfc5646]
	format		= ListField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]
	creator 	= ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created 	= models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime SHOULD timezone.


class Annotation(models.Model):
	jsonld_id   = ListField( models.CharField( max_length = 4096, null = True ) )
	jsonld_type = ListField( models.CharField( max_length = 256 ) )
	body        = ListField( EmbeddedModelField(), null=True )          # CharField( max_length = 4096, null = True )
	target      = ListField( EmbeddedModelField() )                     # models.CharField( max_length = 4096 )
	language 	= models.CharField( max_length = 256, null=True )       # dc:language, [rfc5646]
	format		= models.CharField( max_length = 256, null=True )       # dc:format, [rfc6838]
	creator 	= ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created 	= models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime SHOULD timezone.
	generator 	= ListField( EmbeddedModelField("Agent"), null=True )   # prov:wasGeneratedBy
	generated 	= models.DateTimeField( auto_now=True, null=True )      # prov:generatedAtTime MUST xsd:dateTime SHOULD timezone.
	BOOKMARKING     = "bookmarking"
	CLASSIFYING     = "classifing"
	COMMENTING      = "commenting"
	DESCRIBING      = "describing"
	EDITING         = "editing"
	HIGHLIGHTING    = "highlighting"
	IDENTIFYING     = "identifying"
	LINKING         = "linking"
	MODERATING      = "moderating"
	QUESTIONING     = "questioning"
	REPLYING        = "replying"
	REVIEWING       = "reviewing"
	TAGGING         = "tagging"
	MOTIVATION_CHOICES = (
        (BOOKMARKING,   "oa:bookmarking"), #oa:bookmarking
        (CLASSIFYING,   "oa:classifying"), #oa:classifying
        (COMMENTING,    "oa:commenting"),  #oa:commenting
        (DESCRIBING,    "oa:describing"),  #oa:describing
        (EDITING,       "oa:editing"),     #oa:editing
        (HIGHLIGHTING,  "oa:highlighting"),    #oa:highlighting
        (IDENTIFYING,   "oa:identifying"), #oa:identifying
        (LINKING,       "oa:linking"),     #oa:linking
        (MODERATING,    "oa:moderating"),  #oa:moderating
        (QUESTIONING,   "oa:questioning"), #oa:questioning
        (REPLYING,      "oa:replying"),    #oa:replying
        (REVIEWING,     "oa:reviewing"),   #oa:reviewing
        (TAGGING,       "oa:tagging"),     #oa:tagging
    )
	motivation	= ListField( models.CharField( max_length = 256, choices=MOTIVATION_CHOICES ), null=True )
	# oa:motivatedBy = [oa:Motivation]
	#objects     = MongoDBManager()
    # http://stackoverflow.com/questions/23546480/no-raw-query-method-in-my-django-object
