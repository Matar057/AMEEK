from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.views.generic import TemplateView

from profiles.models import Profile
from profiles.mixins import CarteRequiredMixin
from payments.models import Payment
from events.models import Event
from forum.models import Question
from communication.models import Publication


class DashboardIndexView(CarteRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_members = User.objects.count()
        total_profiles = Profile.objects.count()
        total_mentors = Profile.objects.filter(est_mentor=True).count()
        nouveaux_bacheliers = Profile.objects.filter(
            promotion_bac__isnull=False, promotion_bac__gte=2024,
            profession='', universite=''
        ).count()

        total_payments = Payment.objects.aggregate(total=Sum('montant'))['total'] or 0
        payment_count = Payment.objects.count()

        total_events = Event.objects.count()
        total_questions = Question.objects.count()

        universite_stats = (
            Profile.objects.values('universite')
            .exclude(universite='')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        filiere_stats = (
            Profile.objects.values('filiere')
            .exclude(filiere='')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        recent_members = User.objects.order_by('-date_joined')[:5]
        recent_questions = Question.objects.order_by('-created_at')[:5]
        upcoming_events = Event.objects.filter(est_public=True).order_by('date')[:5]
        recent_publications = Publication.objects.filter(est_public=True)[:3]

        context.update({
            'total_members': total_members,
            'total_profiles': total_profiles,
            'total_mentors': total_mentors,
            'nouveaux_bacheliers': nouveaux_bacheliers,
            'total_payments': total_payments,
            'payment_count': payment_count,
            'total_events': total_events,
            'total_questions': total_questions,
            'universite_stats': universite_stats,
            'filiere_stats': filiere_stats,
            'recent_members': recent_members,
            'recent_questions': recent_questions,
            'upcoming_events': upcoming_events,
            'recent_publications': recent_publications,
        })
        return context
