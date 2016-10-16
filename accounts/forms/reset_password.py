from django import forms
from accounts.models import UserCred, AnnotatorProfile
from django_countries.data import COUNTRIES
from captcha.fields import CaptchaField


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Enter registered email"), max_length=254)


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                    )
        return password2


class AccountRetrieveForm(forms.Form):
    """
    Form for sending known information about account upon lost credentials.
    """
    first_name      = forms.CharField( widget=forms.widgets.TextInput(), label="First name", required=False)
    last_name       = forms.CharField( widget=forms.widgets.TextInput(), label="Last name", required=True)

    contact_email   = forms.EmailField(widget=forms.widgets.TextInput(), label="Contact email", required=False)
    username        = forms.EmailField(widget=forms.widgets.TextInput(), label="Registered email", required=False)

    nickname        = forms.CharField( widget=forms.widgets.TextInput(), label="Annotator pseudonym", required=False)
    job_title       = forms.CharField( widget=forms.widgets.TextInput(), label="Job title", required=False)
    organization    = forms.CharField( widget=forms.widgets.TextInput(), label="Organization", required=False)
    country         = forms.ChoiceField( widget=forms.Select(), choices=sorted(COUNTRIES.items()), required=False)

    captcha = CaptchaField()

    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        cleaned_data = super(AccountRetrieveForm, self).clean()
        return self.cleaned_data