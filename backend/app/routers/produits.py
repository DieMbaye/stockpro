from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Produit
from app.schemas import ProduitCreation, ProduitLecture, ProduitModification
router = APIRouter(prefix="/produits", tags=["Produits"])


@router.post("", response_model=ProduitLecture, status_code=status.HTTP_201_CREATED)
def creer_produit(donnees: ProduitCreation, db: Session = Depends(get_db)):
    existe = db.scalar(select(Produit).where(Produit.nom == donnees.nom))
    if existe:
        raise HTTPException(status_code=409, detail="Un produit avec ce nom existe déjà")

    produit = Produit(**donnees.model_dump())
    db.add(produit)
    db.commit()
    db.refresh(produit)
    return produit


@router.get("", response_model=list[ProduitLecture])
def lister_produits(db: Session = Depends(get_db)):
    return db.scalars(select(Produit).order_by(Produit.nom)).all()

def trouver_produit(produit_id: int, db: Session) -> Produit:
    produit = db.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return produit


@router.get("/{produit_id}", response_model=ProduitLecture)
def lire_produit(produit_id: int, db: Session = Depends(get_db)):
    return trouver_produit(produit_id, db)


@router.patch("/{produit_id}", response_model=ProduitLecture)
def modifier_produit(
    produit_id: int, donnees: ProduitModification, db: Session = Depends(get_db)
):
    produit = trouver_produit(produit_id, db)
    changements = donnees.model_dump(exclude_unset=True, exclude_none=True)

    nouveau_nom = changements.get("nom")
    if nouveau_nom and nouveau_nom != produit.nom:
        existe = db.scalar(select(Produit).where(Produit.nom == nouveau_nom))
        if existe:
            raise HTTPException(status_code=409, detail="Un produit avec ce nom existe déjà")

    for champ, valeur in changements.items():
        setattr(produit, champ, valeur)

    db.commit()
    db.refresh(produit)
    return produit


@router.delete("/{produit_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_produit(produit_id: int, db: Session = Depends(get_db)):
    produit = trouver_produit(produit_id, db)
    if produit.mouvements:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer un produit qui a des mouvements de stock",
        )
    db.delete(produit)
    db.commit()