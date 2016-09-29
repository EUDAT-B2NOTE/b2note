from eve import Eve
from eve_swagger import swagger
from flask import request
from settings import mongo_settings
from collections import OrderedDict
from mongo_support_functions import readyQuerySetValuesForDumpAsJSONLD
from django.conf import settings as global_settings
import json, requests, os


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



def before_returning_items(resource_name, response):
    if isinstance(response, dict):
        if "_items" in response.keys():
            if isinstance(response["_items"], list):
                for doc in response["_items"]:
                    if isinstance(doc, dict):
                        for k2d in ["_etag", "_created", "_id", "_updated", "_links"]:
                            if k2d in doc.keys():
                                del( doc[k2d] )
            print "** *** " * 12
            print json.dumps(readyQuerySetValuesForDumpAsJSONLD( response["_items"] ), indent=2)
            print "** *** " * 12
            response["_items"] = readyQuerySetValuesForDumpAsJSONLD(response["_items"])
            response["@graph"] = response["_items"]
            del response["_items"]
            context_str = open(os.path.join('./static/', 'files/anno_context.jsonld'), 'r').read()
            response["@context"] = json.loads(context_str, object_pairs_hook=OrderedDict)
    #print 'About to return items from "%s" ' % resource_name
    return response


@app.route('/create_annotation', methods=['POST'])
def post_to_django():
    pid = request.values.get('pid_tofeed')
    subject = request.values.get('subject_tofeed')
    # For the production version the url will be pointing to https://b2note.bsc.es/create_annotation
    url = 'https://b2note-dev.bsc.es/interface_main'
    data = {"pid_tofeed": str(pid), "subject_tofeed": str(subject) }
    headers = {'Content-Type':'application/json'}
    r = requests.post(url, data=data, verify=False)
    return str(r.text)


@app.route('/retrieve_annotations', methods=['GET'])
def get_from_django():
    target_id = request.values.get('target_id')
    annotations = RetrieveAnnotations(target_id)
    
    context_str = open(os.path.join(global_settings.STATIC_PATH, 'files/anno_context.jsonld'), 'r').read()

    response = {"@context": json.loads( context_str, object_pairs_hook=OrderedDict ) }

    response["@graph"] = readyQuerySetValuesForDumpAsJSONLD( annotations )
    
    return str(response)



app.on_fetched_resource += before_returning_items


if __name__ == '__main__':
    app.run()