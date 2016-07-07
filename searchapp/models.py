from django.db import models
from djangotoolbox.fields import ListField, SetField, DictField, EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager



class CssStyleSheet(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )
	CSS 			= "CSS style sheet"
	EMBEDDED		= "Embedded content"
	CLASS_CHOICE	= (
		(CSS, 		"CssStylesheet"),	# oa:CssStyle
		(EMBEDDED,	"EmbeddedContent"),	# oa:EmbeddedContent
	)
	type		= ListField( models.CharField( max_length = 32, choices=CLASS_CHOICE) ) # oa:CssStyle
	value		= models.TextField() # rdf:value
	format		= SetField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]


class RequestHeaderState(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("HTTP request state","HttpState"),) )	# oa:HttpRequestState
	value		= models.TextField() # rdf:value


class TimeState(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("Time state","TimeState"),) )	# oa:TimeState
	sourceDate	= SetField( models.DateTimeField(), null=True ) # oa:sourceDate, MUST xsd:dateTime SHOULD timezone.
	cached		= SetField( models.CharField( max_length = 4096 ), null=True ) # oa:cachedSource


class RangeSelector(models.Model):
	type 			= models.CharField(max_length=32,
									   choices=(("Range selector", "RangeSelector"),))  # oa:DataPositionSelector
	startSelector 	= EmbeddedModelField()  # Must be exactly 1 inclusive starting point
	endSelector		= EmbeddedModelField()  # Must be exactly 1 exclusive ending point of same class as startSelector
	refinedBy		= ListField( EmbeddedModelField(), null=True )


class SvgSelector(models.Model):
	type		= models.CharField( max_length = 32,
									choices = (("SVG selector","SvgSelector"),) )
	value		= models.TextField( null=True )	# MAY be exactly 1 then MUST be well formed SVG XML.
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class DataPositionSelector(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("Data position selector","DataPositionSelector"),) )	# oa:DataPositionSelector
	start		= models.PositiveIntegerField() # oa:start
	end			= models.PositiveIntegerField()	# oa:end
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class TextPositionSelector(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("Text position selector","TextPositionSelector"),) )	# oa:TextPositionSelector
	start		= models.PositiveIntegerField()	# oa:start
	end			= models.PositiveIntegerField()	# oa:end
	# [0:2147483647] i.e. with upper-limit 16 bytes per character, max file size of 17179869176 bytes ~ 17 Gb
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class TextQuoteSelector(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("Text quote selector","TextQuoteSelector"),) )	# oa:TextQuoteSelector
	exact		= models.TextField() 								# oa:exact
	prefix		= models.CharField( max_length = 2048, null=True )	# oa:prefix
	suffix		= models.CharField( max_length = 2048, null=True )	# oa:suffix
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class XPathSelector(models.Model):
	type		= models.CharField(max_length=32,
								   choices=(("XPath selector", "XPathSelector"),) )
	value		= models.CharField( max_length = 4096 )
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class CssSelector(models.Model):
	type		= models.CharField( max_length = 32,
									choices = (("CSS selector", "CssSelector"),))
	value		= models.CharField( max_length = 4096 )				# CSS selection path to the Segment
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class FragmentSelector(models.Model):
	type		= models.CharField( max_length = 32,
									   choices = (("Fragment selector","FragmentSelector"),))	# oa:FragmentSelector
	value		= models.CharField( max_length = 4096 )				# rdf:value
	conformsTo	= models.CharField( max_length = 256, null=True )	# dcterms:conformsTo
	refinedBy	= ListField( EmbeddedModelField(), null=True )


class SpecificResource(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )
	type		= models.CharField( max_length = 256,  null=True )	# (rdf:type) oa:SpecificResource
	source		= EmbeddedModelField("ExternalResource") 			# (oa:hasSource)
	ASSESSING 		= "assessing"
	BOOKMARKING 	= "bookmarking"
	CLASSIFYING 	= "classifing"
	COMMENTING 		= "commenting"
	DESCRIBING 		= "describing"
	EDITING 		= "editing"
	HIGHLIGHTING 	= "highlighting"
	IDENTIFYING 	= "identifying"
	LINKING 		= "linking"
	MODERATING 		= "moderating"
	QUESTIONING 	= "questioning"
	REPLYING 		= "replying"
	TAGGING 		= "tagging"
	MOTIVATION_CHOICES = (
		(ASSESSING, 	"assessing"),		# oa:assessing
		(BOOKMARKING, 	"bookmarking"),		# oa:bookmarking
		(CLASSIFYING, 	"classifying"),		# oa:classifying
		(COMMENTING, 	"commenting"),		# oa:commenting
		(DESCRIBING, 	"describing"),		# oa:describing
		(EDITING, 		"editing"),			# oa:editing
		(HIGHLIGHTING, 	"highlighting"),	# oa:highlighting
		(IDENTIFYING, 	"identifying"),		# oa:identifying
		(LINKING, 		"linking"),			# oa:linking
		(MODERATING, 	"moderating"),		# oa:moderating
		(QUESTIONING, 	"questioning"),		# oa:questioning
		(REPLYING, 		"replying"),		# oa:replying
		(TAGGING, 		"tagging"),			# oa:tagging
	)
	purpose		= models.CharField( max_length = 256, choices=MOTIVATION_CHOICES, null=True )
	selector	= ListField( EmbeddedModelField(), null=True )  # oa:hasSelector
	state		= ListField( EmbeddedModelField(), null=True ) 	# oa:hasState
	styleClass	= ListField( models.TextField(), null=True )	# oa:StyleClass
	scope		= ListField( EmbeddedModelField(), null=True )	# oa:hasScope


class Audience(models.Model):
	id  		= models.CharField( max_length=4096, null=True )
	type		= ListField( models.CharField( max_length = 256 ), null=True )	# SHOULD come from the schema.org class structure.
	props 		= DictField( null=True )										# prefixed schema.org's Audience classes


class Agent(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )
	PERSON          = 'Human agent'
	ORGANISATION    = 'Organization agent'
	SOFTWARE        = 'Software agent'
	AGENT_CHOICES = (
        (PERSON, 		'Person'),			# foaf:Person
        (ORGANISATION,	'Organization'),	# foaf:Organization
        (SOFTWARE, 		'Software'),		# prov:SoftwareAgent
    )
	type		= ListField( models.CharField( max_length = 32,
												 choices=AGENT_CHOICES), null=True )
	name		= ListField( models.CharField( max_length = 2048 ), null=True )			# foaf:name
	nickname    = models.CharField( max_length = 2048, null=True )						# foaf:nick
	email		= ListField( models.CharField(max_length = 2048), null=True )			# foaf:mbox
	email_sha1	= ListField( models.CharField(max_length = 2048), null=True )			# sha1 of "mailto:"+foaf:mbox
	homepage	= ListField( models.CharField(max_length = 4096), null=True )			# foaf:homepage


class ResourceSet(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )
	type		= models.CharField( max_length = 32,
									   choices = (
										   ("Holistic set of resources", "Composite"),
										   ("Ordered list of resources", "List"),
										   ("Set of independent resources", "Independents"),
									   ))
	items		= ListField( EmbeddedModelField() ) # oa:item


class Choice(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )
	type		= models.CharField( max_length = 32,
									   choices = (("Ordered list to pick one from", "Choice"),) )	# oa:Choice
	items		= ListField( EmbeddedModelField() ) # oa:memberList


class TextualBody(models.Model):
	id  		= models.CharField( max_length = 4096, null=True )				#"https://b2note.bsc.es/textualbody/" + mongo_uid
	type		= ListField( models.CharField( max_length = 64 ),  null=True )	# rdf:type; oa:TextualBody
	value       = models.TextField() 											# oa:text
	language 	= ListField( models.CharField( max_length = 256 ), null=True )	# dc:language, [rfc5646]
	format		= ListField( models.CharField( max_length = 256 ), null=True )	# dc:format, [rfc6838]
	processingLanguage = models.CharField( max_length = 256, null=True )		#
	LTR 	= "ltr"
	RTL 	= "rtl"
	AUTO	= "auto"
	TEXT_DIRECTION_CHOICES = (
		(LTR,	"ltr" ),
		(RTL,	"rtl" ),
		(AUTO,	"auto"),
	)
	textDirection = models.CharField( max_length = 32, choices=TEXT_DIRECTION_CHOICES, null=True )
	ASSESSING		= "assessing"
	BOOKMARKING		= "bookmarking"
	CLASSIFYING		= "classifing"
	COMMENTING		= "commenting"
	DESCRIBING		= "describing"
	EDITING			= "editing"
	HIGHLIGHTING	= "highlighting"
	IDENTIFYING		= "identifying"
	LINKING			= "linking"
	MODERATING		= "moderating"
	QUESTIONING		= "questioning"
	REPLYING		= "replying"
	TAGGING			= "tagging"
	MOTIVATION_CHOICES = (
		(ASSESSING,		"assessing"),		# oa:assessing
		(BOOKMARKING,	"bookmarking"),		# oa:bookmarking
		(CLASSIFYING,	"classifying"),		# oa:classifying
		(COMMENTING,	"commenting"),		# oa:commenting
		(DESCRIBING,	"describing"),		# oa:describing
		(EDITING,		"editing"),			# oa:editing
		(HIGHLIGHTING,	"highlighting"),	# oa:highlighting
		(IDENTIFYING,	"identifying"),		# oa:identifying
		(LINKING,		"linking"),			# oa:linking
		(MODERATING,	"moderating"),		# oa:moderating
		(QUESTIONING,	"questioning"),		# oa:questioning
		(REPLYING,		"replying"),		# oa:replying
		(TAGGING,		"tagging"),			# oa:tagging
	)
	purpose		= models.CharField( max_length = 256, choices=MOTIVATION_CHOICES, null=True )
	creator		= ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created		= models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime SHOULD timezone.
	modified 	= models.DateTimeField( auto_now=True, null=True )  	# MUST xsd:dateTime with the UTC timezone expressed as "Z".


class ExternalResource(models.Model):
	id  	    = models.CharField( max_length = 4096 )					# can be IRI with fragment component
	DATASET 	= "dataset"
	IMAGE   	= "image"
	VIDEO   	= "video"
	SOUND   	= "sound"
	TEXT    	= "text"
	RESOURCE_TYPE_CHOICES = (
        (DATASET,   "Dataset"),	# dctypes:Dataset
        (IMAGE,     "Image"),	# dctypes:StillImage
        (VIDEO,     "Video"),	# dctypes:MovingImage
        (SOUND,     "Audio"),	# dctypes:Sound
        (TEXT,      "Text"),	# dctypes:Text
    )
	type	    = ListField( models.CharField( max_length = 64, choices=RESOURCE_TYPE_CHOICES), null=True ) #rdf:class
	format		= ListField( models.CharField( max_length = 256 ), null=True )  # dc:format, [rfc6838]
	language 	= ListField( models.CharField( max_length = 256 ), null=True )  # dc:language, [bcp47]
	processingLanguage = models.CharField( max_length = 256, null=True )		#
	LTR 	= "ltr"
	RTL 	= "rtl"
	AUTO	= "auto"
	TEXT_DIRECTION_CHOICES = (
		(LTR,	"ltr"),
		(RTL,	"rtl"),
		(AUTO,	"auto"),
	)
	textDirection	= models.CharField( max_length = 32, choices=TEXT_DIRECTION_CHOICES, null=True )
	accessibility	= ListField( models.CharField( max_length = 256 ), null=True )	# enumerated list of schema.org accessibilityFeature property
	creator 		= ListField( EmbeddedModelField("Agent"), null=True )  			# dcterms:creator
	created 		= models.DateTimeField( auto_now_add=True, null=True )  		# dcterms:created MUST xsd:dateTime SHOULD timezone.
	modified		= models.DateTimeField( auto_now=True, null=True )				# MUST xsd:dateTime with the UTC timezone expressed as "Z".
	rights			= ListField( models.CharField( max_length=4096 ), null=True )  	# MAY be then MUST be an IRI
	canonical 		= models.CharField( max_length=4096, null=True )  				# IRI
	via 			= ListField( models.CharField( max_length=4096, null=True ) )  	# IRIs


class Annotation(models.Model):
	jsonld_context = models.CharField( max_length = 256 ) 				# "http://www.w3.org/ns/anno.jsonld"
																		# 20160706, abremaud@esciencefactory.com
																		# Should allow list of which link string would be one item, however needs
																		# to be string when alone. How compatibility of Django data model
																		# declaration with specification can be obtained is unclear at this point.
	id          = models.CharField( max_length = 4096 )
	type        = ListField( models.CharField( max_length = 256 ) )		# (rdf:type) oa:Annotation and others
	body        = ListField( EmbeddedModelField(), null=True )          # CharField( max_length = 4096, null = True )
	target      = ListField( EmbeddedModelField() )                     # models.CharField( max_length = 4096 )
	language 	= models.CharField( max_length = 256, null=True )       # dc:language, [rfc5646]
	format		= models.CharField( max_length = 256, null=True )       # dc:format, [rfc6838]
	creator 	= ListField( EmbeddedModelField("Agent"), null=True )   # dcterms:creator
	created 	= models.DateTimeField( auto_now_add=True, null=True )  # dcterms:created MUST xsd:dateTime with the UTC timezone expressed as "Z".
	generator 	= ListField( EmbeddedModelField("Agent"), null=True )   # prov:wasGeneratedBy
	generated 	= models.DateTimeField( auto_now_add=True, null=True )  # prov:generatedAtTime MUST xsd:dateTime with the UTC timezone expressed as "Z".
	modified	= models.DateTimeField( auto_now=True, null=True )		# MUST xsd:dateTime with the UTC timezone expressed as "Z".
	audience	= ListField( EmbeddedModelField("Audience"), null=True )
	rights		= ListField( models.CharField( max_length = 4096 ), null=True )	# MAY be then MUST be an IRI
	canonical	= models.CharField( max_length = 4096, null=True )				# IRI
	via			= ListField( models.CharField( max_length = 4096, null=True ) )	# IRIs
	ASSESSING		= "assessing"
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
	TAGGING         = "tagging"
	MOTIVATION_CHOICES = (
		(ASSESSING, 	"assessing"),  		# oa:assessing
        (BOOKMARKING,   "bookmarking"),		#oa:bookmarking
        (CLASSIFYING,   "classifying"),		#oa:classifying
        (COMMENTING,    "commenting"),		#oa:commenting
        (DESCRIBING,    "describing"),		#oa:describing
        (EDITING,       "editing"),			#oa:editing
        (HIGHLIGHTING,  "highlighting"),	#oa:highlighting
        (IDENTIFYING,   "identifying"),		#oa:identifying
        (LINKING,       "linking"),			#oa:linking
        (MODERATING,    "moderating"),		#oa:moderating
        (QUESTIONING,   "questioning"),		#oa:questioning
        (REPLYING,      "replying"),		#oa:replying
        (TAGGING,       "tagging"),			#oa:tagging
    )
	motivation	= ListField( models.CharField( max_length = 256, choices=MOTIVATION_CHOICES ), null=True )	# oa:motivatedBy = [oa:Motivation]
	stylesheet	= EmbeddedModelField( "CssStyleSheet", null=True ) #oa:styledBy
	objects     = MongoDBManager()
    # http://stackoverflow.com/questions/23546480/no-raw-query-method-in-my-django-object
