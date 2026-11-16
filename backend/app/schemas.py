from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, computed_field

class ProduitCreation(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    prix: int = Field(ge=0)
    seuil_alerte: int = Field(default=5, ge=0)


class ProduitLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: str | None
    prix: int
    quantite: int
    seuil_alerte: int
    date_creation: datetime
    @computed_field
    @property
    def en_alerte(self) -> bool:
        return self.quantite < self.seuil_alerte
    
class ProduitModification(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    prix: int | None = Field(default=None, ge=0)
    seuil_alerte: int | None = Field(default=None, ge=0)
    
class MouvementCreation(BaseModel):
    produit_id: int
    type: Literal["entree", "sortie"]
    quantite: int = Field(gt=0)
    motif: str | None = Field(default=None, max_length=255)


class MouvementLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produit_id: int
    type: str
    quantite: int
    motif: str | None
    date: datetime

class TableauDeBord(BaseModel):
    nombre_produits: int
    valeur_totale_stock: int
    nombre_alertes: int
    produits_en_alerte: list[ProduitLecture]
    derniers_mouvements: list[MouvementLecture]