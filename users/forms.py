from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile
import cloudinary
from cloudinary.forms import CloudinaryFileField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import time


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()

        return user
    

    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(label='First Name', max_length=100, required=False)
    last_name = forms.CharField(label='Last Name', max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.email
        self.fields['first_name'].initial = self.instance.first_name
        self.fields['last_name'].initial = self.instance.last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()

        return user


class ProfileUpdateForm(forms.ModelForm):
    
    image = forms.ImageField()

    class Meta:
        model = Profile
        fields = ['image']

    def save(self, commit=True):
        instance = super(ProfileUpdateForm, self).save(commit=False)

        if 'image' in self.cleaned_data:
            try:
                # Reset the file pointer to the beginning of the file
                self.cleaned_data['image'].file.seek(0)

                # Pass the file content to Cloudinary uploader and set public_id
                uploaded_image = cloudinary.uploader.upload(
                    self.cleaned_data['image'].file.read(),
                    public_id=f"profile_pics/{self.cleaned_data['image'].name.split('/')[-1].split('.')[0]}"
                )


                instance.image = uploaded_image['secure_url']

                if commit:
                    instance.save()


            except Exception as e:
                print(f"Error in cloudinary upload: {e}")

        
        return instance
