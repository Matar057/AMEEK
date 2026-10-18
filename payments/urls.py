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
    path('choisir/', views.PaymentChoiceView.as_view(), name='choice'),
    path('payer/', views.PayTechCheckoutView.as_view(), name='paytech_checkout'),
    path('paytech/ipn/', views.PayTechIPNView.as_view(), name='paytech_ipn'),
    path('paytech/success/', views.PayTechSuccessView.as_view(), name='paytech_success'),
    path('paytech/cancel/', views.PayTechCancelView.as_view(), name='paytech_cancel'),
]
