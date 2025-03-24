from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
import logging

from .models import Appointment
from .forms import AppointmentForm

logger = logging.getLogger(__name__)

def home(request):
    """View for the home page"""
    upcoming_appointments = Appointment.objects.filter(
        date_time__gte=timezone.now()
    ).order_by('date_time')[:5]
    
    return render(request, 'appointments/home.html', {
        'upcoming_appointments': upcoming_appointments
    })

class AppointmentListView(ListView):
    """View for listing all appointments"""
    model = Appointment
    context_object_name = 'appointments'
    template_name = 'appointments/appointment_list.html'
    
    def get_queryset(self):
        return Appointment.objects.order_by('date_time')

class AppointmentDetailView(DetailView):
    """View for showing appointment details"""
    model = Appointment
    context_object_name = 'appointment'
    template_name = 'appointments/appointment_detail.html'

class AppointmentCreateView(CreateView):
    """View for creating a new appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Send notifications after the appointment is created
        try:
            self.object.send_notifications()
            messages.success(self.request, 'Appointment created successfully! A confirmation has been sent to your email.')
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
            messages.success(self.request, 'Appointment created successfully! However, there was an issue sending the confirmation email.')
        
        return response

class AppointmentUpdateView(UpdateView):
    """View for updating an existing appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('appointment-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Send notifications after the appointment is updated
        try:
            self.object.send_notifications()
            messages.success(self.request, 'Appointment updated successfully! A confirmation has been sent to your email.')
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
            messages.success(self.request, 'Appointment updated successfully! However, there was an issue sending the confirmation email.')
        
        return response

class AppointmentDeleteView(DeleteView):
    """View for deleting an appointment"""
    model = Appointment
    context_object_name = 'appointment'
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointment-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Appointment deleted successfully!')
        return super().delete(request, *args, **kwargs)