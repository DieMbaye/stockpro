import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Api, Mouvement, Produit } from '../../services/api';

interface FormulaireMouvement {
  produit_id: number | null;
  type: 'entree' | 'sortie';
  quantite: number;
  motif: string | null;
}

@Component({
  selector: 'app-mouvements',
  imports: [DatePipe, FormsModule],
  templateUrl: './mouvements.html',
  styleUrl: '../produits/produits.css',
})
export class Mouvements implements OnInit {
  private api = inject(Api);

  produits = signal<Produit[]>([]);
  mouvements = signal<Mouvement[]>([]);
  message = signal<string | null>(null);
  succes = signal<string | null>(null);
  formulaire: FormulaireMouvement = this.formulaireVide();

  ngOnInit() {
    this.charger();
  }

  charger() {
    this.api.listerProduits().subscribe({
      next: (liste) => this.produits.set(liste),
      error: () => this.message.set('Impossible de charger les produits'),
    });
    this.api.listerMouvements().subscribe({
      next: (liste) => this.mouvements.set(liste),
      error: () => this.message.set('Impossible de charger les mouvements'),
    });
  }

  enregistrer() {
    this.message.set(null);
    this.succes.set(null);

    const produitId = this.formulaire.produit_id;
    if (produitId === null) {
      this.message.set('Choisis un produit');
      return;
    }

    this.api
      .enregistrerMouvement({ ...this.formulaire, produit_id: produitId })
      .subscribe({
        next: () => {
          this.succes.set('Mouvement enregistré ✅');
          this.formulaire = this.formulaireVide();
          this.charger();
        },
        error: (erreur: HttpErrorResponse) => {
          const detail = erreur.error?.detail;
          this.message.set(
            typeof detail === 'string' ? detail : 'Données invalides : vérifie le formulaire',
          );
        },
      });
  }

  nomProduit(id: number): string {
    return this.produits().find((p) => p.id === id)?.nom ?? `Produit n°${id}`;
  }

  private formulaireVide(): FormulaireMouvement {
    return { produit_id: null, type: 'entree', quantite: 1, motif: null };
  }
}