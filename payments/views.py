import io
from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, View, TemplateView

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
import xlsxwriter

from profiles.mixins import CarteRequiredMixin
from .models import Payment
from .forms import PaymentForm
from communication.email_utils import notify_payment_confirmed

MONTHS = [
    ('', 'Tous les mois'), ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
    ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'),
    ('8', 'Août'), ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'),
    ('12', 'Décembre'),
]

YEAR_CHOICES = [(str(y), str(y)) for y in range(2020, date.today().year + 2)]


class PaymentListView(CarteRequiredMixin, LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all().select_related('member')
        return Payment.objects.filter(member=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['total_collected'] = qs.aggregate(total=Sum('montant'))['total'] or 0
        context['payment_count'] = qs.count()
        return context


class PaymentCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:list')

    def form_valid(self, form):
        form.instance.member = self.request.user
        response = super().form_valid(form)
        notify_payment_confirmed(self.object)
        return response


class PaymentReportsView(UserPassesTestMixin, ListView):
    model = Payment
    template_name = 'payments/reports.html'
    context_object_name = 'payments'

    def test_func(self):
        return self.request.user.is_staff

    def dispatch(self, request, *args, **kwargs):
        self.report_type = kwargs.get('type', 'all')
        self.selected_year = request.GET.get('year', str(date.today().year))
        self.selected_month = request.GET.get('month', '')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Payment.objects.all().select_related('member')
        if self.report_type == 'monthly' and self.selected_month:
            qs = qs.filter(
                date_paiement__year=self.selected_year,
                date_paiement__month=self.selected_month,
            )
        elif self.report_type == 'annual':
            qs = qs.filter(date_paiement__year=self.selected_year)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['report_type'] = self.report_type
        context['selected_year'] = self.selected_year
        context['selected_month'] = self.selected_month
        context['month_choices'] = MONTHS
        context['year_choices'] = YEAR_CHOICES
        context['total_collected'] = qs.aggregate(total=Sum('montant'))['total'] or 0
        context['total_members'] = qs.aggregate(count=Count('member', distinct=True))['count'] or 0
        context['total_up_to_date'] = qs.filter(solde_restant=0).aggregate(
            count=Count('member', distinct=True))['count'] or 0
        return context


class ExportPaymentsExcel(LoginRequiredMixin, View):
    def get(self, request):
        qs = Payment.objects.all().select_related('member')
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Paiements')
        bold = workbook.add_format({'bold': True, 'bg_color': '#FF7F00', 'font_color': 'white'})
        headers = ['Date', 'Membre', 'Montant', 'Mode', 'Référence', 'Solde']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
        for row, p in enumerate(qs, 1):
            sheet.write(row, 0, p.date_paiement.strftime('%d/%m/%Y'))
            sheet.write(row, 1, p.member.get_full_name() or p.member.username)
            sheet.write(row, 2, float(p.montant))
            sheet.write(row, 3, p.get_mode_paiement_display())
            sheet.write(row, 4, p.reference)
            sheet.write(row, 5, float(p.solde_restant))
        sheet.set_column(0, 5, 20)
        workbook.close()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={'Content-Disposition': 'attachment; filename="paiements.xlsx"'})


class ExportPaymentsPDF(LoginRequiredMixin, View):
    def get(self, request):
        qs = Payment.objects.all().select_related('member')
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=10*mm, rightMargin=10*mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.Color(1, 0.5, 0), fontSize=16, spaceAfter=10)
        elements = [Paragraph('Rapport des paiements — AMEEK', title_style)]
        data = [['Date', 'Membre', 'Email', 'Montant', 'Mode', 'Référence', 'Solde']]
        total = 0
        for p in qs:
            data.append([
                p.date_paiement.strftime('%d/%m/%Y'),
                str(p.member), p.member.email,
                f'{p.montant} FCFA', p.get_mode_paiement_display(),
                p.reference or '', f'{p.solde_restant} FCFA'
            ])
            total += p.montant
        data.append(['', '', '', f'Total: {total} FCFA', '', '', ''])
        table = Table(data, colWidths=[25*mm, 30*mm, 35*mm, 25*mm, 20*mm, 25*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(1, 0.5, 0)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.Color(1, 0.97, 0.92)]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(1, 0.5, 0)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('SPAN', (0, -1), (2, -1)),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(f'Généré le — {len(qs)} paiement(s)', styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="paiements.pdf"'})


class ReceiptPDF(LoginRequiredMixin, View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if not request.user.is_staff and payment.member != request.user:
            return HttpResponse('Accès non autorisé.', status=403)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(90*mm, 100*mm),
                                leftMargin=4*mm, rightMargin=4*mm,
                                topMargin=4*mm, bottomMargin=4*mm)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=14, leading=16,
                                     textColor=colors.Color(1, 0.5, 0), alignment=TA_CENTER, spaceAfter=3*mm)
        label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=7, leading=9,
                                     textColor=colors.grey)
        value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=8, leading=10)
        recu_style = ParagraphStyle('Recu', parent=styles['Normal'], fontSize=10, leading=12,
                                    textColor=colors.Color(1, 0.5, 0), alignment=TA_CENTER, spaceAfter=2*mm)

        elements = []

        elements.append(Paragraph('AMEEK', title_style))
        elements.append(Paragraph(f'Reçu N° {payment.numero_recu or "---"}', recu_style))
        elements.append(Spacer(1, 2*mm))

        data = [
            [Paragraph('<b>Membre</b>', value_style),
             Paragraph(payment.member.get_full_name() or payment.member.username, value_style)],
            [Paragraph('<b>Montant</b>', value_style),
             Paragraph(f'{payment.montant} FCFA', value_style)],
            [Paragraph('<b>Date</b>', value_style),
             Paragraph(payment.date_paiement.strftime('%d/%m/%Y %H:%M'), value_style)],
            [Paragraph('<b>Mode</b>', value_style),
             Paragraph(payment.get_mode_paiement_display(), value_style)],
        ]
        if payment.reference:
            data.append([Paragraph('<b>Référence</b>', value_style),
                         Paragraph(payment.reference, value_style)])
        data.append([Paragraph('<b>Solde</b>', value_style),
                     Paragraph(f'{payment.solde_restant} FCFA', value_style)])

        table = Table(data, colWidths=[25*mm, 50*mm])
        table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5*mm),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph('Merci pour votre contribution !', ParagraphStyle(
            'Footer', parent=value_style, fontSize=7, textColor=colors.grey, alignment=TA_CENTER)))
        elements.append(Paragraph('Solidarité – Entraide – Respect – Engagement',
                                   ParagraphStyle('Moto', parent=value_style, fontSize=6,
                                                  textColor=colors.Color(1, 0.5, 0), alignment=TA_CENTER)))

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf',
                            headers={'Content-Disposition': f'attachment; filename="recu_{payment.numero_recu or payment.pk}.pdf"'})


class FinancialStatsView(UserPassesTestMixin, TemplateView):
    template_name = 'payments/financial_stats.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_payments = Payment.objects.all()

        total_collected = all_payments.aggregate(total=Sum('montant'))['total'] or 0
        payment_count = all_payments.count()
        member_count = all_payments.aggregate(count=Count('member', distinct=True))['count'] or 0

        mode_stats = (
            all_payments.values('mode_paiement')
            .annotate(total=Sum('montant'), count=Count('id'))
            .order_by('-total')
        )
        for m in mode_stats:
            m['mode_label'] = dict(Payment.MODE_CHOICES).get(m['mode_paiement'], m['mode_paiement'])

        monthly_stats = (
            all_payments
            .annotate(month=TruncMonth('date_paiement'))
            .values('month')
            .annotate(total=Sum('montant'), count=Count('id'))
            .order_by('-month')
        )
        for m in monthly_stats:
            m['month_name'] = [
                '', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ][m['month'].month]
            m['year'] = m['month'].year

        latest_payments = all_payments.select_related('member').order_by('-date_paiement')[:10]

        context.update({
            'total_collected': total_collected,
            'payment_count': payment_count,
            'member_count': member_count,
            'mode_stats': mode_stats,
            'monthly_stats': monthly_stats,
            'latest_payments': latest_payments,
        })
        return context
