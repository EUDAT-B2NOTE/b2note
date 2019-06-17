
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