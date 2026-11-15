import { Routes } from '@angular/router';

import { Produits } from './pages/produits/produits';
import { TableauDeBord } from './pages/tableau-de-bord/tableau-de-bord';
import { Mouvements } from './pages/mouvements/mouvements';

export const routes: Routes = [
  { path: '', component: TableauDeBord },
  { path: 'produits', component: Produits },
  { path: 'mouvements', component: Mouvements },
];