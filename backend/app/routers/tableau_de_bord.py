from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mouvement, Produit
from app.schemas import TableauDeBord

router = APIRouter(prefix="/tableau-de-bord", tags=["Tableau de bord"])


@router.get("", response_model=TableauDeBord)
def tableau_de_bord(db: Session = Depends(get_db)):
    nombre_produits = db.scalar(select(func.count(Produit.id)))

    valeur_totale_stock = db.scalar(
        select(func.coalesce(func.sum(Produit.prix * Produit.quantite), 0))
    )

    produits_en_alerte = db.scalars(
        select(Produit)
        .where(Produit.quantite < Produit.seuil_alerte)
        .order_by(Produit.quantite)
    ).all()

    derniers_mouvements = db.scalars(
        select(Mouvement)
        .order_by(Mouvement.date.desc(), Mouvement.id.desc())
        .limit(5)
    ).all()

    return {
        "nombre_produits": nombre_produits,
        "valeur_totale_stock": valeur_totale_stock,
        "nombre_alertes": len(produits_en_alerte),
        "produits_en_alerte": produits_en_alerte,
        "derniers_mouvements": derniers_mouvements,
    }