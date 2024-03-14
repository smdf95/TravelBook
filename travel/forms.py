from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Trip

class TripCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Create'))


    class Meta:
        model = Trip
        fields = ['title']

class AddTravellerForm(forms.ModelForm):
    travellers = forms.EmailField(label='Traveller Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Trip
        fields = ['travellers']


    def clean_email(self):
        email = self.cleaned_data['travellers']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("This email does not belong to any user.")
        return user.pk
    

class AddViewerForm(forms.ModelForm):
    viewers = forms.EmailField(label='Viewer Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Trip
        fields = ['viewers']


    def clean_email(self):
        email = self.cleaned_data['viewers']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("This email does not belong to any user.")
        return user.pk
    
        