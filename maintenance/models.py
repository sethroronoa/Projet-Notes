import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User


class TicketReparation(models.Model):
    STATUT_CHOICES = [
        ('recu', 'Reçu (En attente)'),
        ('reparation', 'En cours de réparation'),
        ('pret', 'Réparé - Prêt pour retrait'),
        ('livre', 'Livré au client'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    client_nom = models.CharField(max_length=100, default="Client Passage")
    modele_telephone = models.CharField(max_length=100)
    probleme_declare = models.TextField()
    diagnostic_technique = models.TextField(blank=True, null=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='recu')

    def _generate_reference(self):
        year = date.today().strftime('%y')
        count = TicketReparation.objects.count() + 1
        prefix_index = (count - 1) // 999
        first = chr(ord('A') + prefix_index // 26)
        second = chr(ord('A') + prefix_index % 26)
        seq = (count - 1) % 999 + 1
        return f"{first}{second}{year}{seq:03d}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.modele_telephone} - {self.client_nom}"


class PieceDetachee(models.Model):
    nom = models.CharField(max_length=150)
    reference = models.CharField(max_length=50, unique=True)
    quantite_stock = models.PositiveIntegerField(default=0)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom


class Facture(models.Model):
    ticket = models.OneToOneField(TicketReparation, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    piece = models.ForeignKey(PieceDetachee, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
