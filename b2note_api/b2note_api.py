# 04/06/2019 - new Eve schema - for validation of w3c web annotation data model - body
from eve import Eve
import os
string_or_list_of_strings = {'anyof':[
        {'type':'string'},#single string
        {'type':'list','schema':{'type':'string'}}# or list of strings
      ]}

body_type = {
    'id': {'type':'string'},
    'type':{'type':'string','allowed':['Dataset','Image','Video','Sound','Text',  'TextualBody','Choice']}, #W3C list Dataset..Text for external resources, TextualBody,Choicethese values - but may contain other values from vocabularies
    'format':string_or_list_of_strings,
    'language':string_or_list_of_strings,
    'processingLanguage':{'type':'string'},
    'textDirection': {'type':'string','allowed':['ltr','ptr','auto']},
    'value':{'type':'string'}, # in case of type==TextualBody
    'items':{'type':'list','schema':{'type':'string'}} # in case of type==Choice
  }

body_type_or_string = {'anyof': [
      {'type': 'string'}, #single string
      {'type': 'dict', 'schema': body_type}, #single struct
  ]}

body_schema = {'anyof': [
    {'type': 'string'},  # single string
    {'type': 'dict', 'schema': body_type},  # single_struct
    {'type': 'list', 'schema': body_type_or_string}  # list of struct
  ]}
      #'value': {'type': 'string'},
      #'purpose': {'type': 'string'},
      #'type': {
      #  'type': 'list',
      #  'schema': {
      #    'type': 'string',
      #  },
      #},
      #'items': {
      #  'type': 'list',
      #  'schema': {
      #    'type': {'type': 'string'},
      #    'source': {'type': 'string'},
      #    'value': {'type': 'string'}
      #  },
      #},
      # 'language' : {
      #    'type' : 'list',
      #    'schema' : {
      #        'type' : 'string',
      #        },
      #    },
      # 'format' : {
      #    'type' : 'list',
      #    'schema' : {
      #        'type' : 'string',
      #        },
      #    },
      # 'processingLanguage' : { 'type' : 'string' },
      # 'textDirection' : { 'type' : 'string' },
      # 'creator' : {
      #    'type' : 'list',
      #    'schema' : agent,
      #    },
      # 'created' : { 'type' : 'datetime' },
      # 'modified' : { 'type' : 'datetime' },





annotation_schema = {
    '@context': {'type': 'string'},
    'id': {'anyof': [
      {'type': 'string'},
      {'type': 'list', 'schema': {'type': 'string'}}
    ]},
    'body': body_schema,
    'bodyValue': {'type': 'string'},
    'target': {'required': True, 'anyof': [
      {'type': 'string'},
      {'type': 'list', 'schema': {'type': 'string'}}
    ]}
  }

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

app = Eve(settings=my_settings)

if __name__== "__main__":
  print('Instantiating standalone server.')
  app.run()
