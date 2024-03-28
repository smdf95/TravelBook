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
    f_name = forms.CharField(label='First Name', max_length=100)
    l_name = forms.CharField(label='Last Name', max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    class Meta:
        model = User
        fields = ['username', 'email', 'f_name', 'l_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    f_name = forms.CharField(label='First Name', max_length=100)
    l_name = forms.CharField(label='Last Name', max_length=100)
    image = forms.ImageField()

    class Meta:
        model = Profile
        fields = ['f_name', 'l_name', 'image']

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



