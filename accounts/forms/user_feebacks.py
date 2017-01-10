from django import forms
from accounts.models import UserFeedback, FeatureRequest, BugReport
from django_countries.data import COUNTRIES


class FeedbackForm(forms.Form):
    """
    Form for submitting a user feedback.
    """
    eval_overall    = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                        label="Overall notation", initial='5' )
    eval_usefull    = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                         label="Usefulness", initial='5' )
    eval_experience = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                         label="User experience", initial='5' )
    eval_interface  = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                         label="Interface", initial='5' )
    eval_efficiency = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                         label="Efficiency", initial='5' )
    general_comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'maxlength':'5000'}), required=False, label="General comment (<5000 char.)")

    #class Meta:
    #    model   = UserFeedback
    #    fields  = ["eval_overall", "eval_usefull", "eval_experience", "eval_interface", "eval_efficiency", "general_comment" ]
