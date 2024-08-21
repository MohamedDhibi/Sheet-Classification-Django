from django import forms 
from .models import UploadedImage
  
class UploadImageForm(forms.ModelForm): 
  
    class Meta: 
        model = UploadedImage 
        fields = ['image']  # Only include the 'image' field, as 'title' is set automatically
