"""schema definitions for annotation and it's parts

the schema definition is base for validation before a data artefact is stored into MONGODB collection
the schema validation is executed by Eve framework
"""

string_or_list_of_strings = {'anyof': [
    {'type': 'string'},  # single string
    {'type': 'list', 'schema': {'type': 'string'}}  # or list of strings
]}

# W3C list Dataset..Text for external resources, TextualBody,Choicethese values - but may contain other values from vocabularies
body_type_type={'type': 'string',
             'allowed': ['Dataset', 'Image', 'Video', 'Sound', 'Text', 'TextualBody', 'Choice', 'SpecificResource','Composite']}

item_type2={
    'source':{'type':'string'},
    'value':{'type':'string'},
    'type':body_type_type
}

item_schema={'anyof':[
    {'type': 'string'},
    {'type': 'dict', 'schema':item_type2 }
]}

body_type = {
    'id': {'type': 'string'},
    'type': body_type_type,
    'format': string_or_list_of_strings,
    'language': string_or_list_of_strings,
    'processingLanguage': {'type': 'string'},
    'textDirection': {'type': 'string', 'allowed': ['ltr', 'ptr', 'auto']},
    'value': {'type': 'string'},  # in case of type==TextualBody
    'items': {'type': 'list', 'schema': item_schema},  # in case of type==Choice
    'source': {'type': 'string'}
}

body_type_or_string = {'anyof': [
    {'type': 'string'},  # single string
    {'type': 'dict', 'schema': body_type},  # single struct
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

creator_schema = {
    'type': 'dict', 'schema': {
        'id': {'type': 'string'},
        'type': {'type': 'string'},
        'name': {'type': 'string'},
        'nickname': {'type': 'string'}
    }
}

annotation_schema = {
    '@context': {'type': 'string'},
    'id': {'anyof': [
        {'type': 'string'},
        {'type': 'list', 'schema': {'type': 'string'}}
    ]},
    'body': body_schema,
    'bodyValue': {'type': 'string'},
    'target': target_schema,
    'creator': creator_schema
}
