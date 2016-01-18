import json


from .models import *



def CreateFromPOSTinfo( subject_url, object_json ):
    object_uri   = ""
    object_label = ""

    try:

        if subject_url and type(subject_url) is unicode and len(subject_url)>0:

            o = json.loads(object_json)

            if "uris" in o.keys():
                object_uri = o["uris"]
                if "labels" in o.keys(): object_label = o["labels"]

                print object_label, " ", object_uri

                ann = Annotation(\
                        triple=Triple(\
                                subject=TripleElement(iri=subject_url,label="", definition="",curation_status="", ontology_iri="",ontology_shortname="",ontology_version="",),\
                                predicate=TripleElement(iri="http://purl.obolibrary.org/obo/IAO_0000136",label="is about",definition="Is_about is a (currently) primitive relation that relates an information artifact to an entity.",curation_status="pending final vetting",ontology_iri="http://purl.obolibrary.org/obo/iao.owl",ontology_shortname="IAO",ontology_version="2015,02,23",),\
                                object=TripleElement(\
                                        iri     =   object_uri,\
                                        label   =   object_label,\
                                        definition = "",\
                                        curation_status = "",\
                                        ontology_iri = "",\
                                        ontology_shortname= "",\
                                        ontology_version= "",\
                                ),\
                        ),\
                        provenance=Provenance(\
                                createdBy="abremaud@esciencefactory.com",
                        ),\
                ).save()

    except ValueError:

        print "Could not save to DB"
        return Annotation.objects.all()

    print "Created an Annotation"
    return Annotation.objects.all()