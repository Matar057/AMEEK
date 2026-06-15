from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from profiles.mixins import CarteRequiredMixin
from .models import Document
from .forms import DocumentForm


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 15

    def get_queryset(self):
        qs = Document.objects.all()
        if not self.request.user.is_authenticated:
            qs = qs.filter(est_public=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Document.CATEGORY_CHOICES
        return context


class DocumentCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('documents:list')

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if not request.user.is_staff and request.user != doc.uploader:
            messages.error(request, "Vous n'avez pas la permission de modifier ce document.")
            return redirect('documents:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Document modifié avec succès.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('documents:list')


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    success_url = reverse_lazy('documents:list')

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if not request.user.is_staff and request.user != doc.uploader:
            messages.error(request, "Vous n'avez pas la permission de supprimer ce document.")
            return redirect('documents:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Document supprimé.')
        return super().form_valid(form)
