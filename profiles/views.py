import base64
import io
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View, TemplateView
from django.contrib.auth.models import User

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import xlsxwriter
import qrcode

from .models import Profile
from .forms import ProfileForm, ProfileSearchForm
from .mixins import CarteRequiredMixin


class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile') and Profile.objects.filter(user=request.user).exists():
            from django.shortcuts import redirect
            return redirect('profiles:update')
        return super().get(request, *args, **kwargs)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileDetailView(DetailView):
    model = User
    template_name = 'profiles/member_detail.html'
    context_object_name = 'member'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return User.objects.filter(profile__est_visible=True)


class MemberListView(CarteRequiredMixin, ListView):
    model = User
    template_name = 'profiles/member_list.html'
    context_object_name = 'members'
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.filter(profile__est_visible=True).select_related('profile')
        form = ProfileSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            filiere = form.cleaned_data.get('filiere')
            universite = form.cleaned_data.get('universite')
            profession = form.cleaned_data.get('profession')
            if q:
                queryset = queryset.filter(
                    Q(first_name__icontains=q) | Q(last_name__icontains=q) |
                    Q(username__icontains=q)
                )
            if filiere:
                queryset = queryset.filter(profile__filiere__icontains=filiere)
            if universite:
                queryset = queryset.filter(profile__universite__icontains=universite)
            if profession:
                queryset = queryset.filter(profile__profession__icontains=profession)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProfileSearchForm(self.request.GET)
        context['total_members'] = self.get_queryset().count()
        return context


class ExportMembersExcel(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        users = User.objects.filter(profile__est_visible=True).select_related('profile')
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet('Membres')
        bold = workbook.add_format({'bold': True, 'bg_color': '#FF7F00', 'font_color': 'white'})
        headers = ['Nom', 'Prénom', 'Email', 'Bac', 'Série', 'Université', 'Filière', 'Profession', 'Mentor']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, bold)
        for row, user in enumerate(users, 1):
            sheet.write(row, 0, user.last_name)
            sheet.write(row, 1, user.first_name)
            sheet.write(row, 2, user.email)
            sheet.write(row, 3, user.profile.promotion_bac or '')
            sheet.write(row, 4, user.profile.get_serie_display() or '')
            sheet.write(row, 5, user.profile.universite or '')
            sheet.write(row, 6, user.profile.filiere or '')
            sheet.write(row, 7, user.profile.profession or '')
            sheet.write(row, 8, 'Oui' if user.profile.est_mentor else '')
        sheet.set_column(0, 8, 20)
        workbook.close()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={'Content-Disposition': 'attachment; filename="membres.xlsx"'})


class ExportMembersPDF(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        users = User.objects.filter(profile__est_visible=True).select_related('profile')
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=10*mm, rightMargin=10*mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], textColor=colors.Color(1, 0.5, 0), fontSize=16, spaceAfter=10)
        elements = [Paragraph('Liste des membres — AMEEK', title_style)]
        data = [['Nom', 'Prénom', 'Email', 'Bac', 'Série', 'Université', 'Filière', 'Profession', 'Mentor']]
        for u in users:
            data.append([
                u.last_name, u.first_name, u.email,
                str(u.profile.promotion_bac or ''),
                u.profile.get_serie_display() or '',
                u.profile.universite or '', u.profile.filiere or '',
                u.profile.profession or '',
                'Oui' if u.profile.est_mentor else ''
            ])
        table = Table(data, colWidths=[30*mm, 30*mm, 35*mm, 12*mm, 18*mm, 30*mm, 30*mm, 30*mm, 15*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(1, 0.5, 0)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(1, 0.97, 0.92)]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(f'Généré le — {len(users)} membre(s)', styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="membres.pdf"'})


class MemberCardView(CarteRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'profiles/member_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.request.user)

        qr = qrcode.make(self.request.build_absolute_uri(
            reverse_lazy('profiles:member_detail', kwargs={'username': self.request.user.username})
        ))
        buf = BytesIO()
        qr.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        context.update({
            'profile': profile,
            'member': self.request.user,
            'qr_b64': qr_b64,
        })
        return context


class MemberCardPDF(CarteRequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(90*mm, 60*mm),
                                leftMargin=3*mm, rightMargin=3*mm,
                                topMargin=3*mm, bottomMargin=3*mm)

        styles = getSampleStyleSheet()
        style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, leading=10)
        style_name = ParagraphStyle('Name', parent=styles['Normal'], fontSize=12, leading=14,
                                    textColor=colors.Color(1, 0.5, 0), alignment=TA_CENTER)
        style_id = ParagraphStyle('ID', parent=styles['Normal'], fontSize=7, leading=9,
                                  textColor=colors.grey, alignment=TA_CENTER)

        elements = []

        title = Paragraph('AMEEK', style_name)
        elements.append(title)
        elements.append(Spacer(1, 2*mm))

        full_name = user.get_full_name() or user.username
        name_p = Paragraph(full_name, ParagraphStyle('FN', parent=style_normal, fontSize=10,
                                                      alignment=TA_CENTER, spaceAfter=1*mm))
        elements.append(name_p)

        if profile.numero_membre:
            mid = Paragraph(f'N° {profile.numero_membre}', style_id)
            elements.append(mid)

        elements.append(Spacer(1, 2*mm))

        info_lines = []
        if profile.type_membre:
            info_lines.append(f'<b>Type :</b> {profile.type_membre}')
        if profile.universite:
            info_lines.append(f'<b>{profile.universite}</b>')
        if profile.filiere:
            info_lines.append(profile.filiere)
        if profile.profession:
            info_lines.append(profile.profession)

        for line in info_lines:
            elements.append(Paragraph(line, style_normal))

        elements.append(Spacer(1, 2*mm))
        url = request.build_absolute_uri(
            reverse_lazy('profiles:member_detail', kwargs={'username': user.username})
        )
        elements.append(Paragraph(f'<link href="{url}">{url}</link>',
                                  ParagraphStyle('Link', parent=style_normal, fontSize=5, textColor=colors.blue)))

        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)
        elements.append(Spacer(1, 1*mm))
        elements.append(RLImage(qr_buf, width=25*mm, height=25*mm, hAlign='CENTER'))

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf',
                            headers={
                                'Content-Disposition': f'attachment; filename="carte_membre_{user.username}.pdf"'})
