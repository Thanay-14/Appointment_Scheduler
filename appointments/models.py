from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def validate_future_date(value):
    """Validate that appointment date is in the future."""
    if value < timezone.now():
        raise ValidationError('Appointment date cannot be in the past')

class Appointment(models.Model):
    """Model representing an appointment"""
    APPOINTMENT_TYPES = [
        ('CONS', 'Consultation'),
        ('CHKP', 'Checkup'),
        ('FOLW', 'Follow-up'),
        ('EMRG', 'Emergency'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    appointment_type = models.CharField(
        max_length=4,
        choices=APPOINTMENT_TYPES,
        default='CONS'
    )
    date_time = models.DateTimeField(validators=[validate_future_date])
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_time']
    
    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"
    
    def get_absolute_url(self):
        return reverse('appointment-detail', args=[str(self.id)])
    
    def send_notifications(self):
        """Send notifications to AWS services"""
        try:
            from .aws_utils import send_appointment_notification, invoke_lambda_for_appointment
            
            # Send notification via SNS
            send_appointment_notification(self)
            
            # Invoke Lambda function for additional processing
            invoke_lambda_for_appointment(self)
            
            logger.info(f"Notifications sent for appointment ID {self.id}")
        except Exception as e:
            logger.error(f"Failed to send notifications for appointment ID {self.id}: {str(e)}")

def appointment_document_path(instance, filename):
    """Generate path for appointment documents"""
    # Format: appointments/{appointment_id}/{filename}
    return f"appointments/{instance.appointment.id}/{filename}"

class AppointmentDocument(models.Model):
    """Model for documents related to appointments"""
    appointment = models.ForeignKey(Appointment, related_name='documents', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file_url = models.URLField(max_length=255)
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.appointment.title}"
    
    def delete(self, *args, **kwargs):
        """Override delete method to also delete file from S3"""
        try:
            from .aws_utils import delete_file_from_s3
            # Extract filename from URL
            filename = self.file_name
            delete_file_from_s3(filename)
        except Exception as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
        
        # Call the "real" delete method
        super().delete(*args, **kwargs)