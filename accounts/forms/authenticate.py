from django import forms

class AuthenticationForm(forms.Form):
    """
    Login form
    """
    username = forms.EmailField(widget=forms.widgets.TextInput, label="Email")
    password = forms.CharField(widget=forms.widgets.PasswordInput, label="Password")

    class Meta:
        fields = ['username', 'password']

