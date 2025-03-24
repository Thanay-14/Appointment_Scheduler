from django import forms
from .models import Appointment
class AppointmentForm(forms.ModelForm):
    """Form for creating and updating appointments"""
    
    class Meta:
        model = Appointment
        fields = ['title', 'description', 'appointment_type', 'date_time', 
                  'duration', 'name', 'email', 'phone']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_duration(self):
        """Validate duration is between 15 and 120 minutes"""
        duration = self.cleaned_data.get('duration')
        if duration < 15:
            raise forms.ValidationError("Appointments must be at least 15 minutes long")
        if duration > 120:
            raise forms.ValidationError("Appointments cannot exceed 2 hours (120 minutes)")
        return duration