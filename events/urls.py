from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('create/', views.EventCreateView.as_view(), name='create'),
    path('<int:pk>/modifier/', views.EventUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.EventDeleteView.as_view(), name='delete'),
    path('<int:pk>/register/', views.register_event, name='register'),
    path('<int:pk>/unregister/', views.unregister_event, name='unregister'),
    path('<int:pk>/confirmed/', views.RegistrationConfirmedView.as_view(), name='registration_confirmed'),
    path('calendrier/', views.EventCalendarView.as_view(), name='calendar'),
]
