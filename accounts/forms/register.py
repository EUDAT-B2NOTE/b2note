from django import forms
from accounts.models import UserCred, AnnotatorProfile
from django_countries.data import COUNTRIES


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

    class Meta:
        model   = UserCred
        fields  = ['username', 'password1', 'password2',
                   'nickname', 'first_name', 'last_name',
                   'job_title', 'organization', 'annotator_exp',
                   'country']

    def save(self, commit=True):
        print type(self)
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password("password")
        if commit:
            ap = AnnotatorProfile(
                nickname=self.cleaned_data["nickname"],
                first_name=self.data["auth_firstname"],
                last_name=self.data["auth_lastname"],
                email=self.data["auth_email"],
                country=self.cleaned_data["country"],
                organization=self.cleaned_data["organization"],
                job_title=self.cleaned_data["job_title"],
                annotator_exp=self.cleaned_data["annotator_exp"]
            )
            ap.save(using='users')
            user.annotator_id = ap

            user.save(using='users')
        return user

