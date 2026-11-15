import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { Api, ResumeTableauDeBord } from '../../services/api';

@Component({
  selector: 'app-tableau-de-bord',
  imports: [DecimalPipe],
  templateUrl: './tableau-de-bord.html',
  styleUrl: './tableau-de-bord.css',
})
export class TableauDeBord implements OnInit {
  private api = inject(Api);

  donnees = signal<ResumeTableauDeBord | null>(null);
  erreur = signal(false);

  ngOnInit() {
    this.api.tableauDeBord().subscribe({
      next: (resultat) => this.donnees.set(resultat),
      error: () => this.erreur.set(true),
    });
  }
}