from django.db import models
from django.contrib.auth.models import User


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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']

    def __str__(self):
        return f"{self.member.username} - {self.montant} FCFA ({self.date_paiement:%d/%m/%Y})"
