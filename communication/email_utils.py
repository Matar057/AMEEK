from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Notification


def create_notification(user, titre, message, type_notif='info', lien=''):
    Notification.objects.create(
        destinataire=user,
        titre=titre,
        message=message,
        type=type_notif,
        lien=lien,
    )


def send_email_html(to_email, subject, template_name, context):
    context.setdefault('site_name', 'AMEEK')
    context.setdefault('base_url', settings.BASE_URL)
    html = render_to_string(f'communication/emails/{template_name}.html', context)
    text = render_to_string(f'communication/emails/{template_name}.txt', context)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()


def notify_new_message(message):
    url = settings.BASE_URL + reverse('communication:message_detail', args=[message.pk])
    create_notification(
        user=message.destinataire,
        titre='Nouveau message',
        message=f"Vous avez reçu un message de {message.expediteur.get_full_name() or message.expediteur.username} : {message.sujet}",
        type_notif='info',
        lien=url,
    )
    if message.destinataire.email:
        send_email_html(
            to_email=message.destinataire.email,
            subject=f'AMEEK - Nouveau message de {message.expediteur.get_full_name() or message.expediteur.username}',
            template_name='new_message',
            context={
                'prenom': message.destinataire.first_name,
                'expediteur': message.expediteur.get_full_name() or message.expediteur.username,
                'sujet': message.sujet,
                'message': message.corps,
                'url': url,
            },
        )


def notify_new_publication(publication):
    from django.contrib.auth.models import User
    membres = User.objects.filter(is_active=True).exclude(email='')
    url = settings.BASE_URL + reverse('communication:publication_detail', args=[publication.pk])
    for membre in membres:
        create_notification(
            user=membre,
            titre=f'Nouvelle publication : {publication.titre}',
            message=publication.contenu[:200],
            type_notif='info',
            lien=url,
        )
        if membre.email:
            send_email_html(
                to_email=membre.email,
                subject=f'AMEEK - {publication.titre}',
                template_name='new_publication',
                context={
                    'prenom': membre.first_name,
                    'titre': publication.titre,
                    'contenu': publication.contenu,
                    'auteur': publication.auteur.get_full_name() or publication.auteur.username if publication.auteur else 'AMEEK',
                    'url': url,
                },
            )


def notify_mentorship_request(mentorship):
    url = settings.BASE_URL + reverse('mentorship:my_requests')
    create_notification(
        user=mentorship.mentor,
        titre='Nouvelle demande de mentorat',
        message=f"{mentorship.mentee.get_full_name() or mentorship.mentee.username} souhaite être votre mentoré.",
        type_notif='info',
        lien=url,
    )
    if mentorship.mentor.email:
        send_email_html(
            to_email=mentorship.mentor.email,
            subject=f'AMEEK - Nouvelle demande de mentorat',
            template_name='mentorship_request',
            context={
                'prenom': mentorship.mentor.first_name,
                'mentee': mentorship.mentee.get_full_name() or mentorship.mentee.username,
                'message': mentorship.message,
                'url': url,
            },
        )


def notify_mentorship_accepted(mentorship):
    url = settings.BASE_URL + reverse('mentorship:my_requests')
    create_notification(
        user=mentorship.mentee,
        titre='Demande de mentorat acceptée',
        message=f"{mentorship.mentor.get_full_name() or mentorship.mentor.username} a accepté votre demande de mentorat.",
        type_notif='success',
        lien=url,
    )
    if mentorship.mentee.email:
        send_email_html(
            to_email=mentorship.mentee.email,
            subject='AMEEK - Demande de mentorat acceptée',
            template_name='mentorship_accepted',
            context={
                'prenom': mentorship.mentee.first_name,
                'mentor': mentorship.mentor.get_full_name() or mentorship.mentor.username,
                'url': url,
            },
        )


def notify_payment_confirmed(payment):
    url = settings.BASE_URL + reverse('payments:receipt', args=[payment.pk])
    create_notification(
        user=payment.member,
        titre='Paiement confirmé',
        message=f"Votre paiement de {payment.montant} FCFA a été enregistré. Reçu : {payment.numero_recu}.",
        type_notif='success',
        lien=url,
    )
    if payment.member.email:
        send_email_html(
            to_email=payment.member.email,
            subject=f'AMEEK - Confirmation de paiement ({payment.numero_recu})',
            template_name='payment_confirmed',
            context={
                'prenom': payment.member.first_name,
                'montant': payment.montant,
                'numero_recu': payment.numero_recu,
                'date': payment.date_paiement.strftime('%d/%m/%Y %H:%M'),
                'mode': payment.get_mode_paiement_display(),
                'url': url,
            },
        )
