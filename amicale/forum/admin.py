from django.contrib import admin
from .models import Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'est_resolu', 'answer_count', 'created_at')
    list_filter = ('est_resolu',)
    search_fields = ('titre', 'contenu')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'auteur', 'est_solution', 'created_at')
    list_filter = ('est_solution',)
