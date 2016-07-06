from django.db import models
from djangotoolbox.fields import ListField, SetField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager



class Agent(models.Model):
	id 	    = models.CharField( max_length = 4096, null=True ) #"https://b2note.bsc.es/agent/" + mongo_uid
	PERSON          = 'Human agent'
	ORGANISATION    = 'Organization agent'
	SOFTWARE        = 'Software agent'
	AGENT_CHOICES = (
        (PERSON, 		'Person'),			# foaf:Person
        (ORGANISATION,	'Organization'),	# foaf:Organization
        (SOFTWARE, 		'Software'),		# prov:SoftwareAgent
    )
	type	= SetField( models.CharField( max_length = 32,\
												 choices=AGENT_CHOICES), null=True )
	name		= models.CharField( max_length = 2048, null=True ) #foaf:name
	nick	    = models.CharField( max_length = 2048, null=True ) #foaf:nick
	email		= SetField( models.CharField(max_length = 2048), null=True ) #foaf:mbox
	homepage	= SetField( models.CharField(max_length = 4096), null=True ) #foaf:homepage


class List(models.Model):
	type	= models.CharField( max_length = 32, \
									   choices = (("List multiplicity construct","List"),) )	# oa:List
	members		= ListField( EmbeddedModelField() ) # oa:memberList


class Composite(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Composite multiplicity construct","Composite"),) )	# oa:Composite
	item		= ListField( EmbeddedModelField() ) # oa:item


class Choice(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Choice multiplicity construct","Choice"),) )	# oa:Choice
	members		= ListField( EmbeddedModelField() ) # oa:memberList


class CssStyleSheet(models.Model):
	id 		= models.CharField( max_length = 4096, null=True )
	CSS 			= "CSS style sheet"
	EMBEDDED		= "Embedded content"
	CLASS_CHOICE	= (
		(CSS, 		"CssStylesheet"),	# oa:CssStyle
		(EMBEDDED,	"EmbeddedContent"),	# oa:EmbeddedContent
	)
	type = SetField( models.CharField( max_length = 32, choices=CLASS_CHOICE) ) # oa:CssStyle
	value		= models.TextField() # rdf:value
	format		= SetField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]


class RequestHeaderState(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("HTTP request state","HttpState"),) )	# oa:HttpRequestState
	value		= models.TextField() # rdf:value


class TimeState(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Time state","TimeState"),) )	# oa:TimeState
	sourceDate	= SetField( models.DateTimeField(), null=True ) # oa:sourceDate, MUST xsd:dateTime SHOULD timezone.
	cached		= SetField( models.CharField( max_length = 4096 ), null=True ) # oa:cachedSource


class DataPositionSelector(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Data position selector","DataPositionSelector"),) )	# oa:DataPositionSelector
	start		= models.PositiveIntegerField() # oa:start
	end			= models.PositiveIntegerField()	# oa:end


class SvgSelector(models.Model):
	SVG 		= "SVG selector"
	EMBEDDED	= "Embedded content"
	SVG_SELECTOR_TYPE = (
		(SVG, 		"SvgSelector"),		# oa:SvgSelector
		(EMBEDDED,	"EmbeddedContent"),	# oa:EmbeddedContent
	)
	type	= SetField( models.CharField( max_length = 32, choices = SVG_SELECTOR_TYPE ) )
	text		= models.TextField( null=True ) # oa:text
	format		= models.CharField( max_length = 32,\
									  choices = (("SVG media-type","image/svg+xml"),), null=True ) # dc:format


class TextPositionSelector(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Text position selector","TextPositionSelector"),) )	# oa:TextPositionSelector
	start		= models.PositiveIntegerField() # oa:start
	# [0:2147483647] i.e. with upper-limit 16 bytes per character, max file size of 17179869176 bytes ~ 17 Gb
	end			= models.PositiveIntegerField()	# oa:end


class TextQuoteSelector(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Text quote selector","TextQuoteSelector"),) )	# oa:TextQuoteSelector
	exact		= models.TextField() # oa:exact
	prefix		= models.CharField( max_length = 2048, null=True ) # oa:prefix
	suffix		= models.CharField( max_length = 2048, null=True ) # oa:suffix


class FragmentSelector(models.Model):
	type	= models.CharField( max_length = 32,\
									   choices = (("Fragment selector","FragmentSelector"),), null=True )	# oa:FragmentSelector
	value		= models.CharField( max_length = 4096 )	# rdf:value
	conformsTo	= models.CharField( max_length = 256 )	# dcterms:conformsTo


class SpecificResource(models.Model):
	id 	= models.CharField( max_length = 4096, null=True )
	type	= models.CharField( max_length = 64, null=True ) # (rdf:type) oa:SpecificResource
	source		= EmbeddedModelField("ExternalResource") # (oa:hasSource)
	BOOKMARKING     = "bookmarking"
	CLASSIFYING     = "classifying"
	COMMENTING      = "commenting"
	DESCRIBING      = "describing"
	EDITING         = "editing"
	HIGHLIGHTING	= "highlighting"
	IDENTIFYING     = "identifying"
	LINKING         = "linking"
	MODERATING      = "moderating"
	QUESTIONING     = "questioning"
	REPLYING        = "replying"
	REVIEWING       = "reviewing"
	TAGGING         = "tagging"
	MOTIVATION_CHOICES = (
        (BOOKMARKING,   "bookmarking"), #oa:bookmarking
        (CLASSIFYING,   "classifying"), #oa:classifying
        (COMMENTING,    "commenting"),  #oa:commenting
        (DESCRIBING,    "describing"),  #oa:describing
        (EDITING,       "editing"),     #oa:editing
        (HIGHLIGHTING,  "highlighting"),    #oa:highlighting
        (IDENTIFYING,   "identifying"), #oa:identifying
        (LINKING,       "linking"),     #oa:linking
        (MODERATING,    "moderating"),  #oa:moderating
        (QUESTIONING,   "questioning"), #oa:questioning
        (REPLYING,      "replying"),    #oa:replying
        (REVIEWING,     "reviewing"),   #oa:reviewing
        (TAGGING,       "tagging"),     #oa:tagging
    )
	role		= models.CharField( max_length = 256, choices=MOTIVATION_CHOICES, null=True ) # oa:hasRole
	state		= ListField( EmbeddedModelField(), null=True ) 	# oa:hasState
	selector	= EmbeddedModelField( null=True )				# oa:hasSelector
	styleClass	= ListField( models.TextField(), null=True )	# oa:StyleClass
	scope		= ListField( EmbeddedModelField(), null=True )	# oa:hasScope


class TextualBody(models.Model):
	id 	= models.CharField( max_length = 4096, null=True ) #"https://b2note.bsc.es/textualbody/" + mongo_uid
	type	= SetField( models.CharField( max_length = 64 ), null=True ) # rdf:type; oa:TextualBody
	text        = models.TextField() # oa:text
	language 	= SetField( models.CharField( max_length = 256 ), null=True )  # dc:language, [rfc5646]
	format		= SetField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]
	BOOKMARKING     = "bookmarking"
	CLASSIFYING     = "classifying"
	COMMENTING      = "commenting"
	DESCRIBING      = "describing"
	EDITING         = "editing"
	HIGHLIGHTING	= "highlighting"
	IDENTIFYING     = "identifying"
	LINKING         = "linking"
	MODERATING      = "moderating"
	QUESTIONING     = "questioning"
	REPLYING        = "replying"
	REVIEWING       = "reviewing"
	TAGGING         = "tagging"
	MOTIVATION_CHOICES = (
        (BOOKMARKING,   "bookmarking"), #oa:bookmarking
        (CLASSIFYING,   "classifying"), #oa:classifying
        (COMMENTING,    "commenting"),  #oa:commenting
        (DESCRIBING,    "describing"),  #oa:describing
        (EDITING,       "editing"),     #oa:editing
        (HIGHLIGHTING,  "highlighting"),    #oa:highlighting
        (IDENTIFYING,   "identifying"), #oa:identifying
        (LINKING,       "linking"),     #oa:linking
        (MODERATING,    "moderating"),  #oa:moderating
        (QUESTIONING,   "questioning"), #oa:questioning
        (REPLYING,      "replying"),    #oa:replying
        (REVIEWING,     "reviewing"),   #oa:reviewing
        (TAGGING,       "tagging"),     #oa:tagging
    )
	role	= models.CharField( max_length = 256, choices=MOTIVATION_CHOICES, null=True )
	creator = ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created = models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime SHOULD timezone.
	# oa:hasRole = oa:Motivation


class ExternalResource(models.Model):
	id 	= models.CharField( max_length = 4096, null=True )
	DATASET = "dataset"
	IMAGE   = "image"
	VIDEO   = "video"
	SOUND   = "sound"
	TEXT    = "text"
	RESOURCE_TYPE_CHOICES = (
        (DATASET,   "Dataset"),	# dctypes:Dataset
        (IMAGE,     "Image"),	# dctypes:StillImage
        (VIDEO,     "Video"),	# dctypes:MovingImage
        (SOUND,     "Audio"),	# dctypes:Sound
        (TEXT,      "Text"),	# dctypes:Text
    )
	type	= SetField( models.CharField( max_length = 64, choices=RESOURCE_TYPE_CHOICES), null=True ) #rdf:class
	language 	= ListField( models.CharField( max_length = 256 ), null=True )  # dc:language, [rfc5646]
	format		= ListField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]
	creator 	= ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created 	= models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime SHOULD timezone.


class Annotation(models.Model):
	id          = models.CharField( max_length = 4096, null = True )
	type        = SetField( models.CharField( max_length = 256 ) )		# (rdf:type) oa:Annotation and others
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
        (BOOKMARKING,   "bookmarking"), #oa:bookmarking
        (CLASSIFYING,   "classifying"), #oa:classifying
        (COMMENTING,    "commenting"),  #oa:commenting
        (DESCRIBING,    "describing"),  #oa:describing
        (EDITING,       "editing"),     #oa:editing
        (HIGHLIGHTING,  "highlighting"),    #oa:highlighting
        (IDENTIFYING,   "identifying"), #oa:identifying
        (LINKING,       "linking"),     #oa:linking
        (MODERATING,    "moderating"),  #oa:moderating
        (QUESTIONING,   "questioning"), #oa:questioning
        (REPLYING,      "replying"),    #oa:replying
        (REVIEWING,     "reviewing"),   #oa:reviewing
        (TAGGING,       "tagging"),     #oa:tagging
    )
	motivation	= SetField( models.CharField( max_length = 256, choices=MOTIVATION_CHOICES ), null=True )
	# oa:motivatedBy = [oa:Motivation]
	stylesheet	= EmbeddedModelField( "CssStyleSheet", null=True ) #oa:styledBy
	objects     = MongoDBManager()
    # http://stackoverflow.com/questions/23546480/no-raw-query-method-in-my-django-object
