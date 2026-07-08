import logging

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Notification

logger = logging.getLogger(__name__)


def create_notification(user, titre, message, type_notif='info', lien=''):
    Notification.objects.create(
        destinataire=user,
        titre=titre,
        message=message,
        type=type_notif,
        lien=lien,
    )


def send_email_html(to_email, subject, template_name, context):
    if not to_email:
        logger.warning("Tentative d'envoi d'email sans adresse destinataire")
        return False
    try:
        context.setdefault('site_name', 'AMEEK')
        context.setdefault('base_url', settings.BASE_URL)
        html = render_to_string(f'communication/emails/{template_name}.html', context)
        text = render_to_string(f'communication/emails/{template_name}.txt', context)

        api_key = settings.EMAIL_HOST_PASSWORD
        if api_key:
            return _send_via_brevo_api(to_email, subject, html, text, api_key)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()
        logger.info("Email envoyé avec succès à %s — %s", to_email, subject)
        return True
    except BadHeaderError:
        logger.error("En-tête invalide dans l'email à %s — %s", to_email, subject)
    except Exception as e:
        logger.exception("Échec d'envoi d'email à %s — %s", to_email, subject)
    return False


def _send_via_brevo_api(to_email, subject, html, text, api_key):
    from_email = settings.DEFAULT_FROM_EMAIL
    sender_name = "AMEEK"
    sender_email = from_email
    if "<" in from_email and ">" in from_email:
        sender_name = from_email.split("<")[0].strip()
        sender_email = from_email.split("<")[1].rstrip(">")

    payload = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
        "textContent": text,
    }
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers=headers,
        json=payload,
        timeout=15,
    )
    if resp.ok:
        logger.info("Email envoyé via Brevo API à %s — %s", to_email, subject)
        return True
    logger.error(
        "Brevo API error [%s] à %s — %s : %s",
        resp.status_code, to_email, subject, resp.text,
    )
    return False





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


def notify_new_event(event):
    from django.contrib.auth.models import User
    membres = User.objects.filter(is_active=True).exclude(email='')
    url = settings.BASE_URL + reverse('events:detail', args=[event.pk])
    for membre in membres:
        create_notification(
            user=membre,
            titre=f'Nouvel événement : {event.titre}',
            message=f"{event.titre} — {event.date.strftime('%d/%m/%Y %H:%M')} à {event.lieu}",
            type_notif='info',
            lien=url,
        )
        if membre.email:
            send_email_html(
                to_email=membre.email,
                subject=f'AMEEK - Nouvel événement : {event.titre}',
                template_name='new_event',
                context={
                    'prenom': membre.first_name,
                    'titre': event.titre,
                    'description': event.description,
                    'date': event.date.strftime('%d/%m/%Y %H:%M'),
                    'lieu': event.lieu,
                    'url': url,
                },
            )


def notify_event_registration(event, user):
    url = settings.BASE_URL + reverse('events:detail', args=[event.pk])
    create_notification(
        user=user,
        titre='Inscription confirmée',
        message=f"Vous êtes inscrit à l'événement : {event.titre}",
        type_notif='success',
        lien=url,
    )
    if user.email:
        send_email_html(
            to_email=user.email,
            subject=f'AMEEK - Inscription confirmée : {event.titre}',
            template_name='event_registered',
            context={
                'prenom': user.first_name,
                'titre': event.titre,
                'date': event.date.strftime('%d/%m/%Y %H:%M'),
                'lieu': event.lieu,
                'url': url,
            },
        )


def notify_new_offre(offre):
    from django.contrib.auth.models import User
    membres = User.objects.filter(is_active=True).exclude(email='')
    url = settings.BASE_URL + reverse('opportunites:detail', args=[offre.pk])
    for membre in membres:
        create_notification(
            user=membre,
            titre=f'Nouvelle offre : {offre.titre}',
            message=f"{offre.get_type_display()} — {offre.titre}{' — ' + offre.organisation if offre.organisation else ''}",
            type_notif='info',
            lien=url,
        )
        if membre.email:
            send_email_html(
                to_email=membre.email,
                subject=f'AMEEK - Nouvelle offre : {offre.titre}',
                template_name='new_offre',
                context={
                    'prenom': membre.first_name,
                    'titre': offre.titre,
                    'type': offre.get_type_display(),
                    'organisation': offre.organisation or '',
                    'description': offre.description,
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
                'url': url,
            },
        )
