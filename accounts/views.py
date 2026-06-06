from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from .forms import CustomUserCreationForm, CustomAuthenticationForm


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('profiles:buy_card')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post']


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user_obj'

    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user


class AdminUserManagementView(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/admin_users.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return User.objects.all().order_by('-is_superuser', '-is_staff', 'username')


class ToggleAdminView(UserPassesTestMixin, LoginRequiredMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, user_id):
        target = User.objects.get(pk=user_id)
        if target == request.user:
            messages.error(request, 'Vous ne pouvez pas vous retirer vous-même.')
            return redirect('accounts:admin_users')

        target.is_staff = not target.is_staff
        target.is_superuser = target.is_staff
        target.save(update_fields=['is_staff', 'is_superuser'])

        status = 'promu' if target.is_staff else 'rétrogradé'
        messages.success(request, f'{target.username} a été {status}.')

        return redirect('accounts:admin_users')
