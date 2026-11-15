import { DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api, NouveauProduit, Produit } from '../../services/api';

@Component({
  selector: 'app-produits',
  imports: [DecimalPipe, FormsModule],
  templateUrl: './produits.html',
  styleUrl: './produits.css',
})
export class Produits implements OnInit {
  private api = inject(Api);

  produits = signal<Produit[]>([]);
  message = signal<string | null>(null);
  formulaire: NouveauProduit = this.formulaireVide();

  ngOnInit() {
    this.charger();
  }

  charger() {
    this.api.listerProduits().subscribe({
      next: (liste) => this.produits.set(liste),
      error: () => this.message.set('Impossible de charger les produits'),
    });
  }

  ajouter() {
    this.message.set(null);
    this.api.creerProduit(this.formulaire).subscribe({
      next: () => {
        this.formulaire = this.formulaireVide();
        this.charger();
      },
      error: (erreur: HttpErrorResponse) => this.message.set(this.texteErreur(erreur)),
    });
  }

  supprimer(produit: Produit) {
    if (!confirm(`Supprimer « ${produit.nom} » ?`)) {
      return;
    }
    this.message.set(null);
    this.api.supprimerProduit(produit.id).subscribe({
      next: () => this.charger(),
      error: (erreur: HttpErrorResponse) => this.message.set(this.texteErreur(erreur)),
    });
  }

  private formulaireVide(): NouveauProduit {
    return { nom: '', description: null, prix: 0, seuil_alerte: 5 };
  }

  private texteErreur(erreur: HttpErrorResponse): string {
    const detail = erreur.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    return 'Données invalides : vérifie le formulaire';
  }
}