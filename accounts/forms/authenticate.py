from django import forms

class AuthenticationForm(forms.Form):
    """
    Login form
    """
    email = forms.EmailField(widget=forms.widgets.TextInput, label="email")
    password = forms.CharField(widget=forms.widgets.PasswordInput, label="password")

    class Meta:
        fields = ['email', 'password']

