# 04/06/2019 - new Eve schema - for validation of w3c web annotation data model - body
from eve import Eve
from bson import objectid
import os
from eve_swagger import swagger, add_documentation
from b2note_auth import *
from b2note_settings import *

# configures endpoint stored in annotation id's
prefix = '/annotations';
apiurl = 'http://localhost/api';

# if B2NOTE_API_URL is defined then it's used instead of default localhost
if os.environ.get('B2NOTE_API_URL') is not None:
    apiurl = os.environ.get('B2NOTE_API_URL')

# this is custom generation of _id field and duplicates
# the value into id field with url

def addAnnotationId(items):
    print('Adding annotation, adding id')
    for item in items:
        item['_id']=objectid.ObjectId()
        item['id']=apiurl+prefix+'/'+str(item['_id'])
        #print(item)

#preparation for oauth - uncomment if enabled
#app = Eve(settings=b2note_eve_settings,auth=MyBasicAuth)

#unauthenticated instance
app = Eve(settings=b2note_eve_settings)
app.register_blueprint(swagger)
app.config['SWAGGER_INFO'] = b2note_swagger_settings
app.on_insert_annotations += addAnnotationId

if __name__== "__main__":
  print('Instantiating standalone server.')
  app.run()
