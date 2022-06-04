from django import forms
from polls.models import Data, AuthUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email

def updateEmail():
	email = AuthUser.objects.values('email')
	validateEmail = []
	for x in email:
		validateEmail.append(x['email'])
	return validateEmail

def updateUsername():
	username = AuthUser.objects.values('username')
	validateUsername = []
	for x in username:
		validateUsername.append(x['username'])
	return validateUsername

class SignUp(forms.Form):
	email = forms.EmailField(label='email',widget=forms.EmailInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Email'}))
	username = forms.CharField(label='username', max_length=100,widget=forms.TextInput(attrs={'class':'form-control form-control-lg ','placeholder': 'UserName'}))
	fname = forms.CharField(label='FirstName', max_length=100,widget=forms.TextInput(attrs={'class':'form-control form-control-lg ','placeholder': 'First Name'}))
	password = forms.CharField(label='password', max_length=100,widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Password'}))
	lname = forms.CharField(label='LastName', max_length=100,widget=forms.TextInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Last Name'}))
		
	def clean_email(self):
		validateEmail = updateEmail()
		data = self.cleaned_data['email']
		if data in validateEmail:
			raise forms.ValidationError('This email address is already in use.')
		return data
	
	def clean_username(self):
		validateUsername = updateUsername()
		data = self.cleaned_data['username']
		if data in validateUsername:
			raise forms.ValidationError('This username is already in use.')
		return data

	# def save(self, *args, **kwargs):
	# 	print(3)
	# 	self.full_clean
	# 	return super().save(*args,**kwargs)


class Login(forms.Form):
	#email = forms.EmailField(label='email',widget=forms.EmailInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Email'}))
	username = forms.CharField(label='username', max_length=100,widget=forms.TextInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Email or Username'}))
	password = forms.CharField(label='password', max_length=100,widget=forms.PasswordInput(attrs={'class':'form-control form-control-lg ','placeholder': 'Password'}))
	
	def clean(self):
		validateUsername = updateUsername()
		cleanUsername = self.cleaned_data['username']
		if cleanUsername not in validateUsername:
			raise forms.ValidationError('Credentials not found. Please enter again')

		user = AuthUser(email=self.cleaned_data['username'],password = self.cleaned_data['password'])
		if(not user):
			raise forms.ValidationError("Username or password incorrect. Please enter again")
		return 
		