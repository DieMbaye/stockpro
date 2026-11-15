import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

const API_URL = '/api';
export interface Produit {
  id: number;
  nom: string;
  description: string | null;
  prix: number;
  quantite: number;
  seuil_alerte: number;
  date_creation: string;
  en_alerte: boolean;
}

export interface Mouvement {
  id: number;
  produit_id: number;
  type: 'entree' | 'sortie';
  quantite: number;
  motif: string | null;
  date: string;
}

export interface NouveauMouvement {
  produit_id: number;
  type: 'entree' | 'sortie';
  quantite: number;
  motif: string | null;
}

export interface NouveauProduit {
  nom: string;
  description: string | null;
  prix: number;
  seuil_alerte: number;
}

export interface ResumeTableauDeBord {
  nombre_produits: number;
  valeur_totale_stock: number;
  nombre_alertes: number;
  produits_en_alerte: Produit[];
  derniers_mouvements: Mouvement[];
}

@Injectable({ providedIn: 'root' })
export class Api {
  private http = inject(HttpClient);

  tableauDeBord(): Observable<ResumeTableauDeBord> {
    return this.http.get<ResumeTableauDeBord>(`${API_URL}/tableau-de-bord`);
  }
  listerProduits(): Observable<Produit[]> {
  return this.http.get<Produit[]>(`${API_URL}/produits`);
}

creerProduit(produit: NouveauProduit): Observable<Produit> {
  return this.http.post<Produit>(`${API_URL}/produits`, produit);
}

supprimerProduit(id: number): Observable<void> {
  return this.http.delete<void>(`${API_URL}/produits/${id}`);
}
listerMouvements(): Observable<Mouvement[]> {
  return this.http.get<Mouvement[]>(`${API_URL}/mouvements`);
}

enregistrerMouvement(mouvement: NouveauMouvement): Observable<Mouvement> {
  return this.http.post<Mouvement>(`${API_URL}/mouvements`, mouvement);
}
}