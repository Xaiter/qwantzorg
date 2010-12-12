from django.contrib.auth.models import User
from comics.models import UserActivation
from django.core.validators import RegexValidator
from django import forms


class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=128, required=True, error_messages = { 'invalid':'Enter a valid email address.' })   
    password = forms.CharField(max_length=24, widget=forms.PasswordInput, required=True)
    verifyPassword = forms.CharField(max_length=24, widget=forms.PasswordInput, label="Verify Password", required=True)
    activationKey = forms.CharField(max_length=128, widget=forms.HiddenInput, required=True)
    
    def clean(self):        
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        verifyPassword = self.cleaned_data.get("verifyPassword")
        
        if email != None:
            badEmailError = "Wrong email address!"
            try:
                user = User.objects.get(email=email)
                try:
                    record = UserActivation.objects.get(user=user)
                except UserActivation.DoesNotExist:
                    raise forms.ValidationError(badEmailError)
            except User.DoesNotExist:
                raise forms.ValidationError(badEmailError)
                
        
        if password != verifyPassword:
            del self.cleaned_data["password"]
            del self.cleaned_data["verifyPassword"]
            raise forms.ValidationError("The passwords entered did not match!  Try again.")
        
        return self.cleaned_data

class RequestPasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=128, required=True, error_messages = { 'invalid':'Enter a valid email address.' })
    
    def clean(self):
        email = self.cleaned_data.get("email")        
        if email != None:
            try:                            
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No user is associated with that email address.")
            
        return self.cleaned_data            

class CreateComicForm(forms.Form):
    title = forms.CharField(max_length=128, required=True, error_messages = { 'required' : 'Title is required!' })
    panel1Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 1 is required!' })
    panel2Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 2 is required!' })
    panel3Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 3 is required!' })
    panel4Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 4 is required!' })
    panel5Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 5 is required!' })
    panel6Id = forms.IntegerField(required=True, error_messages = { 'required' : 'Panel 6 is required!' })

class CreateAccountForm(forms.Form):
    username = forms.CharField(max_length=24, required=True, validators=[RegexValidator(regex='^[a-zA-Z0-9]+$', message='Usernames must be alphanumeric.', code='invalid')])
    password = forms.CharField(max_length=24, widget=forms.PasswordInput, required=True)
    verifyPassword = forms.CharField(max_length=24, widget=forms.PasswordInput, label="Verify Password", required=True)
    email = forms.EmailField(max_length=128, required=True, error_messages = { 'invalid':'Enter a valid email address.' })
    
    def clean(self):
        password = self.cleaned_data.get("password")
        verifyPassword = self.cleaned_data.get("verifyPassword")
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        
        if password != verifyPassword:
            del self.cleaned_data["password"]
            del self.cleaned_data["verifyPassword"]
            raise forms.ValidationError("The passwords entered did not match!  Try again.")

        if username != None and username != '':
            try:
                user = User.objects.get(username__iexact=username)
                raise forms.ValidationError("Sorry, that username is taken!  Try another.")
            except User.DoesNotExist:
                user = None
                
        if email != None and email != '':
            try:
                user = User.objects.get(email__iexact=email)
                raise forms.ValidationError("This email address has already been used.")
            except User.DoesNotExist:
                user = None
                
        return self.cleaned_data
        