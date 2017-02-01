from eve import Eve
from eve_swagger import swagger
from settings import mongo_settings, virtuoso_settings
from collections import OrderedDict
from jsonld_support_functions import readyQuerySetValuesForDumpAsJSONLD, ridOflistsOfOneItem, orderedJSONLDfields
from jsonld_support_functions import retrieve_annotation_jsonld_from_api, addarobase_totypefieldname, httpPutRdfXmlFileContentToOpenVirtuoso
from django.conf import settings as global_settings
import json, os, copy
import logging

import rdflib
from rdflib import Graph, plugin, term
from rdflib.plugin import Serializer, Parser
rdflib.plugin.register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')
rdflib.plugin.register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')


stdlogger = logging.getLogger('b2note')


app = Eve(settings=mongo_settings)
app.register_blueprint(swagger)


app.config['SWAGGER_INFO'] = {
    'title': 'EUDAT B2Note API',
    'version': '1.0',
    'description': 'EUDAT B2Note API provides read access to annotation documents created using the B2Note web annotator service.',
    'termsOfService': 'EUDAT terms of service',
    'contact': {
        'name': 'B2Note support',
        'url': 'https://github.com/EUDAT-B2NOTE/b2note'
    },
    'license': {
        'name': 'unspecified',
        'url': 'https://github.com/EUDAT-B2NOTE/b2note',
    }
}


# optional. Will use flask.request.host if missing.
#app.config['SWAGGER_HOST'] = 'myhost.com'

# optional. Add/Update elements in the documentation at run-time without deleting subtrees.
# add_documentation({'paths': {'/status': {'get': {'parameters': [
#     {
#         'in': 'query',
#         'name': 'foobar',
#         'required': False,
#         'description': 'special query parameter',
#         'type': 'string'
#     }]
# }}}})



@app.route('/export_to_triplestore')
def export_to_triplestore():
    out = None
    try:
        annL = None
        annL = retrieve_annotation_jsonld_from_api()

        if annL:
            # Replace field name "type" by "@type" for rdflib-jsonld correct processing
            annL = addarobase_totypefieldname(annL)
            # B2SHARE sends fiel urls containing whitespace characters,
            # that rdflib refuses to serialize, replace by %20
            for ann in annL:
                if isinstance(ann, dict):
                    if "target" in ann.keys():
                        if isinstance(ann["target"], dict):
                            if "id" in ann["target"].keys():
                                if isinstance(ann["target"]["id"],(str, unicode)):
                                    if ann["target"]["id"].find(" ")>0:
                                        ann["target"]["id"] = ann["target"]["id"].replace(" ", "%20")
        else:
            print("export_to_triplestore function, no annotation list retrieved.")
            stdlogger.error("export_to_triplestore function, no annotation list retrieved.")
            return None

        g = None
        if annL:
            # Build-up graph from jsonld list of annotations
            g = Graph().parse(data=json.dumps(annL), format='json-ld')
        else:
            print("export_to_triplestore function, no annotation list from addarobase function.")
            stdlogger.error("export_to_triplestore function, no annotation list from addarobase function.")
            return None

        if g:
            # The library adds a trailing slash character to the Software homepage url
            for s, p, o in g.triples((None, None, term.URIRef(u"https://b2note.bsc.es/"))):
                g.add((s, p, term.URIRef(u"https://b2note.bsc.es")))
            for s, p, o in g.triples((None, None, term.URIRef(u"https://b2note.bsc.es/"))):
                g.remove((s, p, term.URIRef(u"https://b2note.bsc.es/")))
        else:
            print("export_to_triplestore function, no graph parsed from json-ld.")
            stdlogger.error("export_to_triplestore function, no graph parsed from json-ld.")
            return None

        files = None
        if g:
            files = g.serialize(format='xml')
        else:
            print("export_to_triplestore function, no graph from removing trailing slash from software homepage url.")
            stdlogger.error("export_to_triplestore function, no graph from removing trailing slash from software homepage url.")
            return None

        R = None
        R = httpPutRdfXmlFileContentToOpenVirtuoso('http://opseudat03.bsc.es:8890/DAV/home/b2note/rdf_sink/test.rdf',
                                                   virtuoso_settings['VIRTUOSO_B2NOTE_USR'],
                                                   virtuoso_settings['VIRTUOSO_B2NOTE_PWD'],
                                                   files)
        if R is not None:
            print "export_to_triplestore function, completed publishing of B2Note annotations to Open Virtuoso triplestore."
            return '''
                <h1>B2NOTE triplestore data update</h1>
                <p>Completed publishing annotations to B2NOTE Open Virtuoso triplestore.</p>
                <p>SPARQL endpoint: <a href="http://opseudat03.bsc.es:8890/sparql" target="_blank">http://opseudat03.bsc.es:8890/sparql</a></p>
                <p>Example query:<p>
                <pre>SELECT DISTINCT ?file ?free_text ?semantic_label
                FROM &#60;urn:dav:home:b2note:rdf_sink>
                WHERE {
                 ?s ?p &#60;http://www.w3.org/ns/oa#Annotation>.
                 ?s &#60;http://www.w3.org/ns/oa#hasTarget> ?file.
                 ?s &#60;http://www.w3.org/ns/oa#hasBody> ?b.
                 OPTIONAL{
                  ?b &#60;http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?free_text.
                 }
                 OPTIONAL{
                  ?b &#60;http://www.w3.org/1999/02/22-rdf-syntax-ns#type> &#60;http://www.w3.org/ns/oa#Composite>.
                  ?b &#60;http://www.w3.org/ns/activitystreams#items> ?d.
                  ?d &#60;http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?e.
                  ?e &#60;http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?f.
                  ?f &#60;http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?semantic_label.
                 }
                }
                LIMIT 50
                </pre>
            '''

        else:
            print "export_to_triplestore function, could not send rdf/xml file content to Open Virtuoso rdf-sink."
            stdlogger.error(
                "export_to_triplestore function, could not send rdf/xml file content to Open Virtuoso rdf-sink.")
            return None

    except:
        print("export_to_triplestore function, did not complete.")
        stdlogger.error("export_to_triplestore function, did not complete.")
        return False

    return out


#@mimerender(default = 'txt', json = render_json, jsonld = render_jsonld, txt = render_txt)
def before_returning_items(response):
    if isinstance(response, dict):
        if "_items" in response.keys():
            if isinstance(response["_items"], list):
                for doc in response["_items"]:
                    if isinstance(doc, dict):
                        for k2d in ["_created", "_etag", "_id", "_links", "_updated"]:
                            if k2d in doc.keys():
                                del( doc[k2d] )
            response["_items"] = readyQuerySetValuesForDumpAsJSONLD(response["_items"])
            response["_items"] = ridOflistsOfOneItem(response["_items"])
            #response = OrderedDict(response)
            response["_items"] = orderedJSONLDfields(response["_items"])
            #response["@graph"] = response["_items"]
            #if not isinstance(response["@graph"], list):
            #    response["@graph"] = [ response["@graph"] ]
            #del(response["_items"])
            #response["@context"] = "jsonld_context_url"#global_settings.JSONLD_CONTEXT_URL
            response["@context"] = {"schema": "http://schema.org"}
            response["@type"] = "ItemList"
            response["schema:itemListElement"] = response["_items"]
            if not isinstance(response["schema:itemListElement"], list):
                response["schema:itemListElement"] = [ response["schema:itemListElement"] ]
            #del(response["_items"])
            for k2d in response.keys():
                if k2d not in ["@type", "schema:itemListElement", "@context", "_etag", "_meta"]:
                    del (response[k2d])
    return response


def before_returning_item(response):
    if isinstance(response, dict):
        resp = copy.deepcopy( response )
        for k2d in ["_created", "_etag", "_id", "_links", "_updated"]:
            if k2d in resp.keys():
                del( resp[k2d] )
        #response["@graph"] = [ readyQuerySetValuesForDumpAsJSONLD( resp ) ]
        #response["@context"] = "jsonld_context_url"#global_settings.JSONLD_CONTEXT_URL
        #response = [ readyQuerySetValuesForDumpAsJSONLD( resp ) ]
        response["_items"] = readyQuerySetValuesForDumpAsJSONLD( resp )
        response["_items"] = ridOflistsOfOneItem( response["_items"] )
        #response = OrderedDict( response )
        response["_items"] = orderedJSONLDfields( response["_items"] )
        response["@context"] = {"schema": "http://schema.org"}
        response["@type"] = "ItemList"
        response["schema:itemListElement"] = response["_items"]

        if not isinstance(response["schema:itemListElement"], list):
            response["schema:itemListElement"] = [response["schema:itemListElement"]]
        for k2d in response.keys():
            if k2d not in ["@type", "schema:itemListElement", "@context", "_etag", "_meta"]:
                del(response[k2d])
    return response


# @app.route('/create_annotation', methods=['POST'])
# def post_to_django():
#     pid = request.values.get('pid_tofeed')
#     subject = request.values.get('subject_tofeed')
#     # For the production version the url will be pointing to https://b2note.bsc.es/create_annotation
#     url = 'https://b2note-dev.bsc.es/interface_main'
#     data = {"pid_tofeed": str(pid), "subject_tofeed": str(subject) }
#     headers = {'Content-Type':'application/json'}
#     r = requests.post(url, data=data, verify=False)
#     return str(r.text)
#
#
# @app.route('/retrieve_annotations', methods=['GET'])
# def get_from_django():
#     target_id = request.values.get('target_id')
#     annotations = RetrieveAnnotations(target_id)
#
#     context_str = open(os.path.join(global_settings.STATIC_PATH, 'files/anno_context.jsonld'), 'r').read()
#
#     response = {"@context": json.loads( context_str, object_pairs_hook=OrderedDict ) }
#
#     response["@graph"] = readyQuerySetValuesForDumpAsJSONLD( annotations )
#
#     return str(response)



app.on_fetched_resource_annotations += before_returning_items
app.on_fetched_item_annotations += before_returning_item


if __name__ == '__main__':
    app.run()