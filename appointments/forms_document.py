# Create a new file named forms_document.py in the appointments directory

from django import forms
from .models import AppointmentDocument

class AppointmentDocumentForm(forms.ModelForm):
    """Form for uploading documents to appointments"""
    
    file = forms.FileField(
        label='Select a file',
        help_text='Max file size: 5MB'
    )
    
    class Meta:
        model = AppointmentDocument
        fields = ['title', 'description', 'file']
    
    def clean_file(self):
        """Validate file size"""
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB")
        return file