from django.urls import path
from . import views
from . import views_document

urlpatterns = [
    path('', views.home, name='home'),
    path('appointments/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/new/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment-delete'),
    path('appointments/<str:appointment_id>/documents/', views_document.AppointmentDocumentListView.as_view(), name='appointment-documents'),
    path('appointments/<str:appointment_id>/documents/upload/', views_document.AppointmentDocumentUploadView.as_view(), name='appointment-document-upload'),
    path('documents/<int:pk>/delete/', views_document.AppointmentDocumentDeleteView.as_view(), name='appointment-document-delete'),
]