import re

from django.db import models
from django.contrib.auth.models import User


def generate_receipt_number():
    last = Payment.objects.filter(numero_recu__isnull=False).order_by('-numero_recu').first()
    if last and last.numero_recu:
        match = re.search(r'(\d+)', last.numero_recu)
        try:
            num = int(match.group(1)) + 1 if match else 1
        except (ValueError, AttributeError):
            num = 1
    else:
        num = 1
    return f'REC-{num:06d}'


class Payment(models.Model):
    MODE_CHOICES = [
        ('especes', 'Espèces'),
        ('virement', 'Virement bancaire'),
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
        ('free_money', 'Free Money'),
        ('carte', 'Carte bancaire'),
        ('autre', 'Autre'),
    ]

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    montant = models.DecimalField('Montant', max_digits=10, decimal_places=0)
    date_paiement = models.DateTimeField('Date de paiement')
    reference = models.CharField('Référence', max_length=100, blank=True)
    mode_paiement = models.CharField('Mode de paiement', max_length=20, choices=MODE_CHOICES)
    solde_restant = models.DecimalField('Solde restant', max_digits=10, decimal_places=0, default=0)
    notes = models.TextField('Notes', blank=True)
    numero_recu = models.CharField('Numéro de reçu', max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']

    def __str__(self):
        return f"{self.member.username} - {self.montant} FCFA ({self.date_paiement:%d/%m/%Y})"

    def save(self, *args, **kwargs):
        if not self.numero_recu:
            self.numero_recu = generate_receipt_number()
        super().save(*args, **kwargs)
