from eve import Eve
from eve_swagger import swagger
from settings import mongo_settings
from collections import OrderedDict
from jsonld_support_functions import readyQuerySetValuesForDumpAsJSONLD
from django.conf import settings as global_settings
import json, os, copy


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



#@mimerender(default = 'txt', json = render_json, jsonld = render_jsonld, txt = render_txt)
def before_returning_items(response):
    if isinstance(response, dict):
        if "_items" in response.keys():
            if isinstance(response["_items"], list):
                for doc in response["_items"]:
                    if isinstance(doc, dict):
                        for k2d in ["_etag", "_created", "_id", "_updated", "_links"]:
                            if k2d in doc.keys():
                                del( doc[k2d] )
            response["_items"] = readyQuerySetValuesForDumpAsJSONLD(response["_items"])
            response["@graph"] = response["_items"]
            if not isinstance(response["@graph"], list):
                response["@graph"] = [ response["@graph"] ]
            del(response["_items"])
            response["@context"] = global_settings.JSONLD_CONTEXT_URL
    return response


def before_returning_item(response):
    if isinstance(response, dict):
        resp = copy.deepcopy( response )
        for k2d in ["_created", "_id", "_updated", "_links", "_etag"]:
            if k2d in resp.keys():
                del( resp[k2d] )
        response["@graph"] = [ readyQuerySetValuesForDumpAsJSONLD( resp ) ]
        response["@context"] = global_settings.JSONLD_CONTEXT_URL
        for k2d in response.keys():
            if k2d not in ["@graph", "@context", "_etag"]:
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