from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='list'),
    path('upload/', views.DocumentCreateView.as_view(), name='upload'),
    path('<int:pk>/modifier/', views.DocumentUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.DocumentDeleteView.as_view(), name='delete'),
]
