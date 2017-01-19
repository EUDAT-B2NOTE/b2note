from django import forms
from accounts.models import UserCred, AnnotatorProfile
from django_countries.data import COUNTRIES
from captcha.fields import CaptchaField


class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    username  = forms.EmailField(widget=forms.widgets.TextInput(), label="Email")
    password1 = forms.CharField(widget=forms.widgets.PasswordInput(), label="Password")
    password2 = forms.CharField(widget=forms.widgets.PasswordInput(), label="Password (again)")

    nickname        = forms.CharField( widget=forms.widgets.TextInput(), label="Annotator pseudonym")
    first_name      = forms.CharField( widget=forms.widgets.TextInput(), label="First name")
    last_name       = forms.CharField( widget=forms.widgets.TextInput(), label="Last name")
    job_title       = forms.CharField( widget=forms.widgets.TextInput(), label="Job title")
    organization    = forms.CharField( widget=forms.widgets.TextInput(), label="Organization")
    country         = forms.ChoiceField( widget=forms.Select(), choices=sorted(COUNTRIES.items()) )
    annotator_exp   = forms.ChoiceField( widget=forms.Select(), choices=[('b','Beginner'),('i','Intermediate'),('e','Expert')], label="Annotator experience")

    captcha = CaptchaField()

    class Meta:
        model   = UserCred
        fields  = ['username', 'password1', 'password2',
                   'nickname', 'first_name', 'last_name',
                   'job_title', 'organization', 'annotator_exp',
                   'country', 'captcha']

    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        cleaned_data = super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
        return self.cleaned_data


    def save(self, commit=True):
        print type(self)
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            ap = AnnotatorProfile(
                nickname=self.cleaned_data["nickname"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                email=self.cleaned_data["username"],
                country=self.cleaned_data["country"],
                organization=self.cleaned_data["organization"],
                job_title=self.cleaned_data["job_title"],
                annotator_exp=self.cleaned_data["annotator_exp"]
            )
            ap.save(using='users')
            user.annotator_id = ap

            user.save(using='users')
        return user

