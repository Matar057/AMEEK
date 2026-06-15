from django.urls import path
from . import views

app_name = 'opportunites'

urlpatterns = [
    path('', views.OffreListView.as_view(), name='list'),
    path('<int:pk>/', views.OffreDetailView.as_view(), name='detail'),
    path('creer/', views.OffreCreateView.as_view(), name='create'),
    path('<int:pk>/modifier/', views.OffreUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.OffreDeleteView.as_view(), name='delete'),
]
