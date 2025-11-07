from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username','email','password1','password2')
class DownloadForm(forms.Form):
    url = forms.CharField(label='URL', max_length=500, widget=forms.TextInput(attrs={'placeholder':'Pega la URL o URI de la playlist'}) )
