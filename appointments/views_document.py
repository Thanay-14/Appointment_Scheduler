# Add to the existing views.py file or create a new file named views_document.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.generic import FormView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Appointment, AppointmentDocument
from .forms_document import AppointmentDocumentForm
from .aws_utils import upload_file_to_s3

import uuid
import logging

logger = logging.getLogger(__name__)

class AppointmentDocumentUploadView(FormView):
    """View for uploading documents to an appointment"""
    form_class = AppointmentDocumentForm
    template_name = 'appointments/document_upload.html'
    
    def get_appointment(self):
        """Get the appointment associated with this upload"""
        appointment_id = self.kwargs.get('appointment_id')
        return get_object_or_404(Appointment, id=appointment_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.get_appointment()
        return context
    
    def form_valid(self, form):
        try:
            appointment = self.get_appointment()
            
            # Get the uploaded file
            uploaded_file = self.request.FILES['file']
            
            # Generate a unique filename
            file_extension = uploaded_file.name.split('.')[-1]
            filename = f"appointments/{appointment.id}/{str(uuid.uuid4())}.{file_extension}"
            
            # Upload file to S3
            file_url = upload_file_to_s3(
                uploaded_file,
                filename,
                content_type=uploaded_file.content_type
            )
            
            # Create document record
            document = form.save(commit=False)
            document.appointment = appointment
            document.file_url = file_url
            document.file_name = filename
            document.save()
            
            messages.success(self.request, 'Document uploaded successfully!')
            return redirect('appointment-detail', pk=appointment.id)
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            messages.error(self.request, f"Error uploading document: {str(e)}")
            return self.form_invalid(form)

class AppointmentDocumentListView(ListView):
    """View for listing documents associated with an appointment"""
    model = AppointmentDocument
    template_name = 'appointments/document_list.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        appointment_id = self.kwargs.get('appointment_id')
        self.appointment = get_object_or_404(Appointment, id=appointment_id)
        return AppointmentDocument.objects.filter(appointment=self.appointment)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.appointment
        return context

class AppointmentDocumentDeleteView(DeleteView):
    """View for deleting a document"""
    model = AppointmentDocument
    template_name = 'appointments/document_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('appointment-documents', kwargs={'appointment_id': self.object.appointment.id})