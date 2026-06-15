from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='list'),
    path('ask/', views.QuestionCreateView.as_view(), name='ask'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('<int:pk>/supprimer/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('<int:pk>/answer/', views.AnswerCreateView.as_view(), name='answer'),
    path('answer/<int:pk>/modifier/', views.AnswerUpdateView.as_view(), name='answer_update'),
    path('answer/<int:pk>/supprimer/', views.AnswerDeleteView.as_view(), name='answer_delete'),
    path('answer/<int:pk>/accept/', views.accept_solution, name='accept_solution'),
]
