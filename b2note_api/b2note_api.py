# 04/06/2019 - new Eve schema - for validation of w3c web annotation data model - body
from eve import Eve
from bson import objectid
import os

# configures endpoint stored in annotation id's
prefix = '/annotations';
apiurl = 'http://localhost/api';
# if B2NOTE_API_URL is defined then it's used instead of default localhost
if os.environ.get('B2NOTE_API_URL') is not None:
    apiurl = os.environ.get('B2NOTE_API_URL')

# schemas for annotations and parts

string_or_list_of_strings = {'anyof':[
        {'type':'string'},#single string
        {'type':'list','schema':{'type':'string'}}# or list of strings
      ]}

body_type = {
    'id': {'type':'string'},
    'type':{'type':'string','allowed':['Dataset','Image','Video','Sound','Text', 'TextualBody','Choice','SpecificResource']}, #W3C list Dataset..Text for external resources, TextualBody,Choicethese values - but may contain other values from vocabularies
    'format':string_or_list_of_strings,
    'language':string_or_list_of_strings,
    'processingLanguage':{'type':'string'},
    'textDirection': {'type':'string','allowed':['ltr','ptr','auto']},
    'value':{'type':'string'}, # in case of type==TextualBody
    'items':{'type':'list','schema':{'type':'string'}}, # in case of type==Choice
    'source':{'type':'string'}
  }

body_type_or_string = {'anyof': [
      {'type': 'string'}, #single string
      {'type': 'dict', 'schema': body_type}, #single struct
  ]}

target_schema = {'required': True,
                 'anyof': [
    {'type': 'string'},  # single string
    {'type': 'dict', 'schema': body_type},  # single_struct
    {'type': 'list', 'schema': body_type_or_string}  # list of struct
  ]}
body_schema = {'anyof': [
    {'type': 'string'},  # single string
    {'type': 'dict', 'schema': body_type},  # single_struct
    {'type': 'list', 'schema': body_type_or_string}  # list of struct
  ]}

annotation_schema = {
    '@context': {'type': 'string'},
    'id': {'anyof': [
      {'type': 'string'},
      {'type': 'list', 'schema': {'type': 'string'}}
    ]},
    'body': body_schema,
    'bodyValue': {'type': 'string'},
    'target': target_schema
  }

# setting for Eve framework and mongodb connection
my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': os.environ['MONGODB_NAME'],
    'MONGO_USERNAME': os.environ['MONGODB_USR'],
    'MONGO_PASSWORD': os.environ['MONGODB_PWD'],
    'DOMAIN': {'annotations': {'allow_unknown': True, 'schema': annotation_schema}},
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],
    'XML': False
  }


# this is custom generation of _id field and duplicates
# the value into id field with url

def addAnnotationId(items):
    print('Adding annotation, adding id')
    for item in items:
        item['_id']=objectid.ObjectId()
        item['id']=apiurl+prefix+'/'+str(item['_id'])
        #print(item)



app = Eve(settings=my_settings)

# register the addAnnotationId as insert hook

app.on_insert_annotations += addAnnotationId

if __name__== "__main__":
  print('Instantiating standalone server.')
  app.run()
