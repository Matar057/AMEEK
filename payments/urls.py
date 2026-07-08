from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='list'),
    path('add/', views.PaymentCreateView.as_view(), name='add'),
    path('reports/', views.PaymentReportsView.as_view(), name='reports'),
    path('reports/<str:type>/', views.PaymentReportsView.as_view(), name='reports_filtered'),
    path('recu/<int:pk>/', views.ReceiptPDF.as_view(), name='receipt'),
    path('statistiques/', views.FinancialStatsView.as_view(), name='stats'),
    path('export/excel/', views.ExportPaymentsExcel.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPaymentsPDF.as_view(), name='export_pdf'),
    path('choisir/', views.PaymentMethodChoiceView.as_view(), name='choice'),
    path('paydunya/checkout/', views.PayDunyaCheckoutView.as_view(), name='paydunya_checkout'),
    path('paydunya/ipn/', views.PayDunyaIPNView.as_view(), name='paydunya_ipn'),
    path('paydunya/success/', views.PayDunyaSuccessView.as_view(), name='paydunya_success'),
    path('paydunya/cancel/', views.PayDunyaCancelView.as_view(), name='paydunya_cancel'),
]
