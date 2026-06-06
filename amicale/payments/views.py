import io
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, View

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import xlsxwriter

from .models import Payment
from .forms import PaymentForm

MONTHS = [
    ('', 'Tous les mois'), ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'),
    ('4', 'Avril'), ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'),
    ('8', 'Août'), ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'),
    ('12', 'Décembre'),
]

YEAR_CHOICES = [(str(y), str(y)) for y in range(2020, date.today().year + 2)]


class PaymentListView(LoginRequiredMixin, ListView):
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


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payments:list')

    def form_valid(self, form):
        form.instance.member = self.request.user
        return super().form_valid(form)


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
                p.date.strftime('%d/%m/%Y'),
                str(p.member), p.member.email,
                f'{p.montant} FCFA', p.get_mode_display(),
                p.reference or '', f'{p.solde} FCFA'
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
