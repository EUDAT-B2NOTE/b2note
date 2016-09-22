from eve import Eve
from flask import request
from settings import mongo_settings
from collections import OrderedDict
from b2note_app.mongo_support_functions import RetrieveAnnotations, readyQuerySetValuesForDumpAsJSONLD
from django.conf import settings as global_settings
import json, requests, os

app = Eve(settings=mongo_settings)


@app.route('/create_annotation', methods=['POST'])
def post_to_django():
    pid = request.values.get('pid_tofeed')
    subject = request.values.get('subject_tofeed')
    # For the production version the url will be pointing to https://b2note.bsc.es/create_annotation
    url='https://b2note-dev.bsc.es/interface_main'
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

if __name__ == '__main__':
    app.run()
