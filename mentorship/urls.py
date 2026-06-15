from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.MentorListView.as_view(), name='mentor_list'),
    path('mine/', views.MyMentorshipsView.as_view(), name='my_requests'),
    path('request/<str:username>/', views.MentorshipRequestView.as_view(), name='request'),
    path('<int:pk>/', views.MentorshipDetailView.as_view(), name='detail'),
    path('<int:pk>/respond/', views.MentorshipResponseView.as_view(), name='respond'),
    path('<int:pk>/delete/', views.MentorshipDeleteView.as_view(), name='delete'),
]
