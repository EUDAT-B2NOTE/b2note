from django import forms
from accounts.models import UserFeedback, FeatureRequest, BugReport
from captcha.fields import CaptchaField


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

    captcha = CaptchaField()


class FeatureForm(forms.Form):
    """
    Form for submitting a feature request.
    """
    title               = forms.CharField(widget=forms.widgets.TextInput(attrs={'maxlength':'100'}), required=False, label="Title (<100 char.)")
    short_description   = forms.CharField(widget=forms.widgets.Textarea(attrs={'maxlength':'5000'}), required=False, label="Short description (<5000 char.)")
    extra_description   = forms.CharField(widget=forms.widgets.Textarea(), required=False, label="Extra information")
    alt_contact         = forms.CharField(widget=forms.widgets.TextInput(attrs={'maxlength':'500'}), required=False, label="Alternative contact")

    captcha = CaptchaField()


class BugReportForm(forms.Form):
    """
    Form for submitting a bug report.
    """

    affected_function   = forms.ChoiceField( widget=forms.Select(), required=False, choices=[
        ('Generic', 'generic bug'),
        ('Create', 'Create annotation'),
        ('Edit', 'Edit annotation'),
        ('Export', 'Export annotation'),
        ('Search', 'Search annotation'),
        ('Other', 'Other functionality')],
                                             label="Affected functionality", initial='5' )
    short_description   = forms.CharField(widget=forms.widgets.Textarea(attrs={'maxlength':'5000'}), required=False, label="Problem description (<5000 char.)")
    extra_description   = forms.CharField(widget=forms.widgets.Textarea(), required=False, label="Extra information")
    browser             = forms.CharField(widget=forms.widgets.TextInput(attrs={'maxlength':'100'}), required=False, label="Title (<200 char.)")
    severity            = forms.ChoiceField( widget=forms.Select(), required=False, choices=[('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)],
                                         label="Severity", initial='5' )
    alt_contact         = forms.CharField(widget=forms.widgets.TextInput(attrs={'maxlength':'500'}), required=False, label="Alternative contact")

    captcha = CaptchaField()

