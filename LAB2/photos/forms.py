from django import forms
# from django.forms import ModelForm

from models import Photo

class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)
    public = forms.BooleanField(initial=False, 
        label='Picture is public?', required=False)
    name = forms.CharField(required=True, max_length=50)