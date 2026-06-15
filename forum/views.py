from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from profiles.mixins import CarteRequiredMixin
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm


class QuestionListView(ListView):
    model = Question
    template_name = 'forum/question_list.html'
    context_object_name = 'questions'
    paginate_by = 15

    def get_queryset(self):
        return Question.objects.all().select_related('auteur')


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'forum/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer_form'] = AnswerForm()
        return context


class QuestionCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'forum/question_form.html'
    success_url = reverse_lazy('forum:list')

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)


class AnswerCreateView(CarteRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = AnswerForm

    def form_valid(self, form):
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        form.instance.question = question
        form.instance.auteur = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forum:detail', kwargs={'pk': self.kwargs['pk']})


def accept_solution(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user == answer.question.auteur:
        Answer.objects.filter(question=answer.question).update(est_solution=False)
        answer.est_solution = True
        answer.save()
        answer.question.est_resolu = True
        answer.question.save()
    return redirect('forum:detail', pk=answer.question.pk)


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'forum/question_form.html'

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        if not request.user.is_staff and request.user != question.auteur:
            messages.error(request, "Vous n'avez pas la permission de modifier cette question.")
            return redirect('forum:detail', pk=question.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Question modifiée avec succès.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forum:detail', kwargs={'pk': self.object.pk})


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    success_url = reverse_lazy('forum:list')

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        if not request.user.is_staff and request.user != question.auteur:
            messages.error(request, "Vous n'avez pas la permission de supprimer cette question.")
            return redirect('forum:detail', pk=question.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Question supprimée.')
        return super().form_valid(form)


class AnswerUpdateView(LoginRequiredMixin, UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'forum/answer_form.html'

    def dispatch(self, request, *args, **kwargs):
        answer = self.get_object()
        if not request.user.is_staff and request.user != answer.auteur:
            messages.error(request, "Vous n'avez pas la permission de modifier cette réponse.")
            return redirect('forum:detail', pk=answer.question.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Réponse modifiée avec succès.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forum:detail', kwargs={'pk': self.object.question.pk})


class AnswerDeleteView(LoginRequiredMixin, DeleteView):
    model = Answer

    def dispatch(self, request, *args, **kwargs):
        answer = self.get_object()
        if not request.user.is_staff and request.user != answer.auteur:
            messages.error(request, "Vous n'avez pas la permission de supprimer cette réponse.")
            return redirect('forum:detail', pk=answer.question.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Réponse supprimée.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forum:detail', kwargs={'pk': self.object.question.pk})
