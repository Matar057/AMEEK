from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from .models import Mentorship
from .forms import MentorshipRequestForm, MentorshipResponseForm


class MentorListView(ListView):
    model = User
    template_name = 'mentorship/mentor_list.html'
    context_object_name = 'mentors'
    paginate_by = 12

    def get_queryset(self):
        return User.objects.filter(profile__est_mentor=True, profile__est_visible=True).select_related('profile')


class MentorshipRequestView(LoginRequiredMixin, CreateView):
    model = Mentorship
    form_class = MentorshipRequestForm
    template_name = 'mentorship/request_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.mentor = get_object_or_404(User, username=self.kwargs['username'])
        if request.user == self.mentor:
            return redirect('profiles:member_detail', username=self.mentor.username)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.mentee = self.request.user
        form.instance.mentor = self.mentor
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mentor'] = self.mentor
        return context

    def get_success_url(self):
        return reverse_lazy('mentorship:my_requests')


class MyMentorshipsView(LoginRequiredMixin, ListView):
    model = Mentorship
    template_name = 'mentorship/my_mentorships.html'
    context_object_name = 'mentorships'

    def get_queryset(self):
        return Mentorship.objects.filter(
            Q(mentor=self.request.user) | Q(mentee=self.request.user)
        ).select_related('mentor', 'mentee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['as_mentor'] = [m for m in context['mentorships'] if m.mentor == self.request.user]
        context['as_mentee'] = [m for m in context['mentorships'] if m.mentee == self.request.user]
        return context


class MentorshipResponseView(LoginRequiredMixin, UpdateView):
    model = Mentorship
    form_class = MentorshipResponseForm
    template_name = 'mentorship/response_form.html'
    success_url = reverse_lazy('mentorship:my_requests')

    def get_queryset(self):
        return Mentorship.objects.filter(mentor=self.request.user)


class MentorshipDetailView(LoginRequiredMixin, DetailView):
    model = Mentorship
    template_name = 'mentorship/detail.html'
    context_object_name = 'mentorship'

    def get_queryset(self):
        return Mentorship.objects.filter(
            Q(mentor=self.request.user) | Q(mentee=self.request.user)
        ).select_related('mentor', 'mentee')
