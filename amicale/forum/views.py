from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

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


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'forum/question_form.html'
    success_url = reverse_lazy('forum:list')

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)


class AnswerCreateView(LoginRequiredMixin, CreateView):
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
