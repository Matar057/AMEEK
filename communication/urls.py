from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Publications
    path('publications/', views.PublicationListView.as_view(), name='publication_list'),
    path('publications/<int:pk>/', views.PublicationDetailView.as_view(), name='publication_detail'),
    path('publications/creer/', views.PublicationCreateView.as_view(), name='publication_create'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/lire/', views.NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('notifications/tout-lire/', views.NotificationMarkAllReadView.as_view(), name='notification_mark_all_read'),

    # Messages
    path('messages/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('messages/envoyes/', views.MessageSentView.as_view(), name='message_sent'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/ecrire/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/supprimer/', views.MessageDeleteView.as_view(), name='message_delete'),
]
