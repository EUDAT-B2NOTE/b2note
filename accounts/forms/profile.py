from django import forms
from accounts.models import AnnotatorProfile
from django_countries.data import COUNTRIES


class ProfileForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    nickname        = forms.CharField( widget=forms.widgets.TextInput(), label="Annotator pseudonym" )
    first_name      = forms.CharField( widget=forms.widgets.TextInput(), label="First name" )
    last_name       = forms.CharField( widget=forms.widgets.TextInput(), label="Last name" )
    email           = forms.EmailField( widget=forms.widgets.TextInput(), label="Email" )
    annotator_exp   = forms.ChoiceField( widget=forms.Select(), choices=[('b', 'Beginner'),
                                                                      ('i', 'Intermediate'),
                                                                      ('e', 'Expert')],
                                        label="Annotator experience" )
    job_title       = forms.CharField( widget=forms.widgets.TextInput(), label="Job title" )
    organization    = forms.CharField( widget=forms.widgets.TextInput(), label="Organization" )
    country         = forms.CharField( widget=forms.widgets.TextInput(), label="Country" )

    class Meta:
        model   = AnnotatorProfile
        fields  = ['nickname', 'email', 'first_name', 'last_name', 'annotator_exp', 'job_title', 'organization', 'country']
