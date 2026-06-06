from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='list'),
    path('ask/', views.QuestionCreateView.as_view(), name='ask'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/answer/', views.AnswerCreateView.as_view(), name='answer'),
    path('answer/<int:pk>/accept/', views.accept_solution, name='accept_solution'),
]
