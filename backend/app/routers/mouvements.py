from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mouvement, Produit
from app.schemas import MouvementCreation, MouvementLecture

router = APIRouter(prefix="/mouvements", tags=["Mouvements"])


@router.post("", response_model=MouvementLecture, status_code=status.HTTP_201_CREATED)
def enregistrer_mouvement(donnees: MouvementCreation, db: Session = Depends(get_db)):
    produit = db.get(Produit, donnees.produit_id, with_for_update=True)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    if donnees.type == "entree":
        produit.quantite += donnees.quantite
    else:
        if donnees.quantite > produit.quantite:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuffisant : il reste {produit.quantite} unité(s)",
            )
        produit.quantite -= donnees.quantite

    mouvement = Mouvement(**donnees.model_dump())
    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)
    return mouvement


@router.get("", response_model=list[MouvementLecture])
def lister_mouvements(produit_id: int | None = None, db: Session = Depends(get_db)):
    requete = select(Mouvement).order_by(Mouvement.date.desc(), Mouvement.id.desc())
    if produit_id is not None:
        requete = requete.where(Mouvement.produit_id == produit_id)
    return db.scalars(requete).all()