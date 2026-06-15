from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from profiles.mixins import CarteRequiredMixin
from .models import Offre
from .forms import OffreForm
from communication.email_utils import notify_new_offre


class OffreListView(ListView):
    model = Offre
    template_name = 'opportunites/offre_list.html'
    context_object_name = 'offres'
    paginate_by = 15

    def get_queryset(self):
        qs = Offre.objects.all()
        type_filter = self.request.GET.get('type')
        if type_filter in dict(Offre.TYPE_CHOICES):
            qs = qs.filter(type=type_filter)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_choices'] = Offre.TYPE_CHOICES
        context['selected_type'] = self.request.GET.get('type', '')
        return context


class OffreDetailView(DetailView):
    model = Offre
    template_name = 'opportunites/offre_detail.html'
    context_object_name = 'offre'


class OffreCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Offre
    form_class = OffreForm
    template_name = 'opportunites/offre_form.html'
    success_url = reverse_lazy('opportunites:list')

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        notify_new_offre(self.object)
        messages.success(self.request, 'Offre publiée avec succès.')
        return response


class OffreUpdateView(LoginRequiredMixin, UpdateView):
    model = Offre
    form_class = OffreForm
    template_name = 'opportunites/offre_form.html'

    def dispatch(self, request, *args, **kwargs):
        offre = self.get_object()
        if not request.user.is_staff and request.user != offre.auteur:
            messages.error(request, "Vous n'avez pas la permission de modifier cette offre.")
            return redirect('opportunites:detail', pk=offre.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Offre modifiée avec succès.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('opportunites:detail', kwargs={'pk': self.object.pk})


class OffreDeleteView(LoginRequiredMixin, DeleteView):
    model = Offre
    success_url = reverse_lazy('opportunites:list')

    def dispatch(self, request, *args, **kwargs):
        offre = self.get_object()
        if not request.user.is_staff and request.user != offre.auteur:
            messages.error(request, "Vous n'avez pas la permission de supprimer cette offre.")
            return redirect('opportunites:detail', pk=offre.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Offre supprimée.')
        return super().form_valid(form)
