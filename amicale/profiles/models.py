from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    SERIE_CHOICES = [
        ('S', 'Scientifique'),
        ('L', 'Littéraire'),
        ('ES', 'Économique et Social'),
        ('STMG', 'STMG'),
        ('STI2D', 'STI2D'),
        ('AUTRE', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    numero_membre = models.CharField('Numéro de membre', max_length=20, unique=True, blank=True, null=True)
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    photo = models.ImageField('Photo', upload_to='photos/', blank=True)
    promotion_bac = models.IntegerField('Promotion du Bac', null=True, blank=True)
    serie = models.CharField('Série du Bac', max_length=10, choices=SERIE_CHOICES, blank=True)
    universite = models.CharField('Université / École', max_length=200, blank=True)
    filiere = models.CharField('Filière d\'étude', max_length=200, blank=True)
    profession = models.CharField('Profession', max_length=200, blank=True)
    bio = models.TextField('Biographie / Conseils', blank=True)
    adresse = models.TextField('Adresse', blank=True)
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    est_mentor = models.BooleanField('Peut être mentor', default=False)
    est_visible = models.BooleanField('Profil visible', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'
        ordering = ['-created_at']

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    @property
    def type_membre(self):
        if self.profession and self.profession.strip():
            return 'Professionnel'
        if self.universite and self.universite.strip():
            return 'Étudiant'
        if self.promotion_bac and self.promotion_bac >= 2024:
            return 'Nouveau bachelier'
        return 'Diplômé'


def generate_member_number():
    last = Profile.objects.filter(numero_membre__isnull=False).order_by('-numero_membre').first()
    if last and last.numero_membre:
        try:
            num = int(last.numero_membre.split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return f'AMK-{num:06d}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.numero_membre = generate_member_number()
        profile.save(update_fields=['numero_membre'])


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
