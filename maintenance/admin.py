from django.contrib import admin
from .models import TicketReparation, PieceDetachee, Facture, LigneFacture

admin.site.register(TicketReparation)
admin.site.register(PieceDetachee)
admin.site.register(Facture)
admin.site.register(LigneFacture)