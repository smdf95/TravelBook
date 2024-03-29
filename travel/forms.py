from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import InlineField, Div
from .models import Trip, Post, Comment, Reply
import cloudinary
from cloudinary import uploader
from cloudinary.forms import CloudinaryFileField

class TripCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Create'))
        


    class Meta:
        model = Trip
        fields = ['title', 'image', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super(TripCreateForm, self).save(commit=False)

        if 'image' in self.cleaned_data:
            try:
                # Reset the file pointer to the beginning of the file
                self.cleaned_data['image'].file.seek(0)

                # Pass the file content to Cloudinary uploader and set public_id
                uploaded_image = uploader.upload(
                    self.cleaned_data['image'].file.read(),
                    public_id=f"trip_pics/{self.cleaned_data['image'].name.split('/')[-1].split('.')[0]}"
                )

                instance.image = uploaded_image['secure_url']

                if commit:
                    instance.save()

            except Exception as e:
                print(f"Error in cloudinary upload: {e}")

        if not instance.image:
            try:
                default_image = uploader.upload(
                    open('path_to_default_image/default.png', 'rb'),  # Provide the path to your default.png
                    public_id="trip_pics/default"
                )
                instance.image = default_image['secure_url']

                if commit:
                    instance.save()

            except Exception as e:
                print(f"Error setting default image: {e}")

        return instance
    


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
    

class PostCreateForm(forms.ModelForm):

    location = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'id': 'searchTextField'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('content', css_class='form-control'),
            Field('image', css_class='form-control'),
            Field('location', css_class='form-control', id='searchTextField'),
            Submit('submit', 'Submit', css_class='btn btn-outline-info')
        )


    class Meta:
        model = Post
        fields = ['content', 'image', 'location']

    def save(self, commit=True):
        instance = super(PostCreateForm, self).save(commit=False)

        if 'image' in self.cleaned_data:
            try:
                # Reset the file pointer to the beginning of the file
                self.cleaned_data['image'].file.seek(0)

                # Pass the file content to Cloudinary uploader and set public_id
                uploaded_image = cloudinary.uploader.upload(
                    self.cleaned_data['image'].file.read(),
                    public_id=f"post_pics/{self.cleaned_data['image'].name.split('/')[-1].split('.')[0]}"
                )


                instance.image = uploaded_image['secure_url']

                if commit:
                    instance.save()


            except Exception as e:
                print(f"Error in cloudinary upload: {e}")

        
        return instance

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your comment here...',
            'rows': 4,
            'cols': 250,
            'style': 'resize:none;'
        })

    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Add Comment',
        }

class ReplyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your reply here...',
            'rows': 2,
            'cols': 150,
            'style': 'resize:none;'
        })

    class Meta:
        model = Reply
        fields = ['content']
       

    
        