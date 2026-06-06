import calendar
from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from .models import Event
from .forms import EventForm


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        return Event.objects.filter(est_public=True).prefetch_related('participants')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_registered'] = self.request.user in self.get_object().participants.all()
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:list')

    def form_valid(self, form):
        form.instance.organisateur = self.request.user
        return super().form_valid(form)


def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.is_authenticated:
        if request.user in event.participants.all():
            messages.info(request, f"Vous êtes déjà inscrit à {event.titre}")
        elif event.places_restantes is None or event.places_restantes > 0:
            event.participants.add(request.user)
            return redirect('events:registration_confirmed', pk=pk)
        else:
            messages.error(request, "Cet événement est complet.")
    return redirect('events:detail', pk=pk)


def unregister_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.is_authenticated:
        event.participants.remove(request.user)
        messages.success(request, f"Vous êtes désinscrit de {event.titre}")
    return redirect('events:detail', pk=pk)


class RegistrationConfirmedView(LoginRequiredMixin, TemplateView):
    template_name = 'events/registration_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        if self.request.user not in event.participants.all():
            messages.error(self.request, "Vous n'êtes pas inscrit à cet événement.")
        context['event'] = event
        return context


class EventCalendarView(ListView):
    model = Event
    template_name = 'events/event_calendar.html'
    context_object_name = 'events'

    def dispatch(self, request, *args, **kwargs):
        today = date.today()
        self.selected_year = int(request.GET.get('year', today.year))
        self.selected_month = int(request.GET.get('month', today.month))
        self.selected_month = max(1, min(12, self.selected_month))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(
            est_public=True,
            date__year=self.selected_year,
            date__month=self.selected_month,
        ).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(self.selected_year, self.selected_month)

        events_by_day = {}
        for e in self.get_queryset():
            day = e.date.day
            events_by_day.setdefault(day, []).append(e)

        today = date.today()
        context.update({
            'selected_year': self.selected_year,
            'selected_month': self.selected_month,
            'month_name': calendar.month_name[self.selected_month],
            'month_days': month_days,
            'events_by_day': events_by_day,
            'prev_month': self.selected_month - 1 if self.selected_month > 1 else 12,
            'prev_year': self.selected_year if self.selected_month > 1 else self.selected_year - 1,
            'next_month': self.selected_month + 1 if self.selected_month < 12 else 1,
            'next_year': self.selected_year if self.selected_month < 12 else self.selected_year + 1,
            'is_current_month': self.selected_year == today.year and self.selected_month == today.month,
            'today': today,
            'month_range': range(1, 13),
            'year_range': range(today.year - 5, today.year + 3),
        })
        return context
