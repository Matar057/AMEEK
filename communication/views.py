from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages as flash_messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import FormMixin

from profiles.mixins import CarteRequiredMixin
from .models import Publication, Notification, Message
from .forms import PublicationForm, MessageForm
from .email_utils import notify_new_message, notify_new_publication


class PublicationListView(ListView):
    model = Publication
    template_name = 'communication/publication_list.html'
    context_object_name = 'publications'
    paginate_by = 12

    def get_queryset(self):
        qs = Publication.objects.select_related('auteur')
        t = self.request.GET.get('type', '')
        if t in dict(Publication.TYPE_CHOICES):
            qs = qs.filter(type=t)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_type'] = self.request.GET.get('type', '')
        context['type_choices'] = Publication.TYPE_CHOICES
        return context


class PublicationDetailView(DetailView):
    model = Publication
    template_name = 'communication/publication_detail.html'
    context_object_name = 'pub'


class PublicationCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = 'communication/publication_form.html'
    success_url = reverse_lazy('communication:publication_list')

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        response = super().form_valid(form)
        notify_new_publication(self.object)
        return response


class NotificationListView(CarteRequiredMixin, LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'communication/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(destinataire=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_queryset().filter(lu=False).count()
        return context


class NotificationMarkReadView(CarteRequiredMixin, LoginRequiredMixin, DetailView):
    model = Notification

    def get(self, request, *args, **kwargs):
        notif = self.get_object()
        if notif.destinataire == request.user and not notif.lu:
            notif.lu = True
            notif.save()
        if notif.lien:
            return redirect(notif.lien)
        return redirect('communication:notification_list')


class NotificationMarkAllReadView(CarteRequiredMixin, LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
        return redirect('communication:notification_list')


class MessageInboxView(CarteRequiredMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = 'communication/message_inbox.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        return Message.objects.filter(destinataire=self.request.user).select_related('expediteur')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_queryset().filter(lu=False).count()
        return context


class MessageSentView(CarteRequiredMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = 'communication/message_sent.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        return Message.objects.filter(expediteur=self.request.user).select_related('destinataire')


class MessageDetailView(CarteRequiredMixin, LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'communication/message_detail.html'
    context_object_name = 'msg'

    def get(self, request, *args, **kwargs):
        msg = self.get_object()
        if msg.destinataire == request.user and not msg.lu:
            msg.lu = True
            msg.lu_le = timezone.now()
            msg.save()
        return super().get(request, *args, **kwargs)


class MessageCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'communication/message_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        to = self.request.GET.get('to', '')
        if to:
            initial['destinataire'] = to
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(is_active=True).values_list('username', flat=True)
        return context

    def form_valid(self, form):
        form.instance.expediteur = self.request.user
        response = super().form_valid(form)
        notify_new_message(self.object)
        flash_messages.success(self.request, 'Message envoyé avec succès.')
        return response

    def get_success_url(self):
        return reverse_lazy('communication:message_sent')


class MessageDeleteView(CarteRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Message

    def get_success_url(self):
        return reverse_lazy('communication:message_inbox')

    def dispatch(self, request, *args, **kwargs):
        msg = self.get_object()
        if msg.destinataire != request.user and msg.expediteur != request.user:
            flash_messages.error(request, "Vous n'avez pas accès à ce message.")
            return redirect('communication:message_inbox')
        if msg.expediteur == request.user:
            flash_messages.success(request, 'Message supprimé.')
        return super().dispatch(request, *args, **kwargs)
