from django import forms
from accounts.models import UserFedback, FeatureRequest, BugReport
from django_countries.data import COUNTRIES


class FeedbackForm(forms.ModelForm):
    """
    Form for submitting a user feedback.
    """
    eval_overall    = forms.CharField( widget=forms.Select(choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),)),
                                         label="Overall notation" ),
    eval_usefull    = forms.ChoiceField( widget=forms.Select, choices=(('1', 1), ('2', 2), ('3', 3), ('4',4), ('5',5),),
                                         label="Usefulness" ),
    eval_experience = forms.ChoiceField( widget=forms.Select(), choices=[('1', 1), ('2', 2), ('3', 3), ('4',4), ('5',5)],
                                         label="User experience" ),
    eval_interface  = forms.ChoiceField( widget=forms.Select(), choices=[('1', 1), ('2', 2), ('3', 3), ('4',4), ('5',5)],
                                         label="Interface" ),
    eval_efficiency = forms.ChoiceField( widget=forms.Select(), choices=[('1', 1), ('2', 2), ('3', 3), ('4',4), ('5',5)],
                                         label="Efficiency" ),
    general_comment = forms.CharField(widget=forms.widgets.TextInput(), label="General comment")

    class Meta:
        model   = UserFedback
        fields  = ["eval_overall", "eval_usefull", "eval_experience", "eval_interface", "eval_efficiency", "general_comment" ]
