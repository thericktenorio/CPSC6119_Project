from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.models import User
from .models import OrgUser
from django import forms
from .patterns.factories import UserFactory

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label = "", max_length = 20, widget = forms.TextInput(attrs = {'class':'form-control', 'placeholder':'First Name'})) 
    last_name = forms.CharField(label = "", max_length = 20, widget = forms.TextInput(attrs = {'class':'form-control', 'placeholder':'Last Name'}))
    email = forms.EmailField(label = "", widget = forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email'}))
    role = forms.ChoiceField(label = "Select Role", choices = OrgUser.USER_ROLES, widget = forms.Select(attrs = {'class':'form-control'}))
    class Meta:
        model = OrgUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
            'role'
        )


    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<ul class = "form-text text-muted small"><li>Username must 20 characters or less.</li><li>Username may contain a combination of letters, numbers and special characters.</li></ul>'
        '<span class = "form-text text-muted"><small>Username must be 20 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class = "form-text text-muted small"><li>Refrain from using easily recognizable or commonly used passwords.</li><li>Password must contain at least 8 characters.</li><li>Password cannot be entirely numeric.</li></ul>' 

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class = "form-text text-muted"<small></small></span>'
    

    def save(self, commit = True):
        user_data = {
            'username' : self.cleaned_data['username'],
            'password' : self.cleaned_data['password1'],
            'first_name' : self.cleaned_data['first_name'],
            'last_name' : self.cleaned_data['last_name'],
            'email' : self.cleaned_data['email'],
        }
        role = self.cleaned_data['role']
        user = UserFactory.create_user(role, **user_data)
        return user
        