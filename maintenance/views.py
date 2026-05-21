import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import TicketReparation, PieceDetachee, Facture


def dashboard(request):
    return render(request, 'maintenance/dashboard.html', {
        'tickets': TicketReparation.objects.all(),
        'statuts': TicketReparation.STATUT_CHOICES,
        'stats': {
            'total':      TicketReparation.objects.count(),
            'recu':       TicketReparation.objects.filter(statut='recu').count(),
            'reparation': TicketReparation.objects.filter(statut='reparation').count(),
            'pret':       TicketReparation.objects.filter(statut='pret').count(),
        }
    })


@require_POST
def ajouter_ticket(request):
    data = json.loads(request.body)
    prob = data.get('probleme', '').lower()
    prix_estime = 1500
    if 'ecran' in prob or 'screen' in prob:
        prix_estime = 6500
    elif 'batterie' in prob or 'battery' in prob:
        prix_estime = 3500
    TicketReparation.objects.create(
        client_nom=data.get('client_nom', 'Client').strip() or 'Client',
        modele_telephone=data.get('modele'),
        probleme_declare=data.get('probleme'),
        prix_total=prix_estime,
        statut='recu',
    )
    return JsonResponse({'success': True})


@require_POST
def edit_ticket_details(request, pk):
    data = json.loads(request.body)
    ticket = get_object_or_404(TicketReparation, pk=pk)
    ticket.client_nom = data.get('client_nom', ticket.client_nom)
    ticket.modele_telephone = data.get('modele')
    ticket.probleme_declare = data.get('probleme')
    ticket.save()
    return JsonResponse({'success': True})


@require_POST
def modifier_statut(request):
    data = json.loads(request.body)
    ticket = get_object_or_404(TicketReparation, id=data.get('ticket_id'))
    ticket.statut = data.get('statut')
    ticket.save()
    return JsonResponse({'success': True})


@require_POST
def supprimer_ticket(request):
    data = json.loads(request.body)
    get_object_or_404(TicketReparation, id=data.get('ticket_id')).delete()
    return JsonResponse({'success': True})


def suivre_ticket(request):
    ticket = None
    erreur = None
    reference_recherche = ''
    if request.method == 'POST':
        reference_recherche = request.POST.get('reference', '').strip().upper()
        try:
            ticket = TicketReparation.objects.get(reference=reference_recherche)
        except TicketReparation.DoesNotExist:
            erreur = f"Aucun ticket trouvé avec la référence « {reference_recherche} »."
        except Exception:
            erreur = "Référence invalide."
    return render(request, 'maintenance/suivre_ticket.html', {
        'ticket': ticket,
        'erreur': erreur,
        'reference_recherche': reference_recherche,
    })


def inventaire(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'ajouter':
            PieceDetachee.objects.create(
                nom=request.POST.get('nom', '').strip(),
                reference=request.POST.get('reference', '').strip(),
                prix_unitaire=request.POST.get('prix_unitaire', 0),
                quantite_stock=request.POST.get('quantite_stock', 0),
            )
        elif action == 'supprimer':
            get_object_or_404(PieceDetachee, id=request.POST.get('piece_id')).delete()
        return redirect('maintenance:inventaire')
    return render(request, 'maintenance/inventaire.html', {
        'pieces': PieceDetachee.objects.all()
    })


def generer_facture_pdf(request, pk):
    ticket = get_object_or_404(TicketReparation, pk=pk)
    facture, _ = Facture.objects.get_or_create(ticket=ticket)
    template = get_template('maintenance/facture_template.html')
    html = template.render({'ticket': ticket, 'facture': facture})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response
