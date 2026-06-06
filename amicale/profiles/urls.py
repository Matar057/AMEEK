from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='profiles:member_list'), name='index'),
    path('create/', views.ProfileCreateView.as_view(), name='create'),
    path('update/', views.ProfileUpdateView.as_view(), name='update'),
    path('membres/', views.MemberListView.as_view(), name='member_list'),
    path('membres/<slug:username>/', views.ProfileDetailView.as_view(), name='member_detail'),
    path('export/excel/', views.ExportMembersExcel.as_view(), name='export_members_excel'),
    path('export/pdf/', views.ExportMembersPDF.as_view(), name='export_members_pdf'),
    path('carte/', views.MemberCardView.as_view(), name='member_card'),
    path('carte/pdf/', views.MemberCardPDF.as_view(), name='card_pdf'),
]
