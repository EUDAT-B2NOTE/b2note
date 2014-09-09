from django import forms
from query.models import Ontologies

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='txt, pdf and xls files accepted'
    )

class OntologyForm(forms.Form):
    name = ( 'EnvThes',
             'BioOntology')
    name = []
    onto = Ontologies.objects.all()
    for i in onto: 
        name.append(i.name)
