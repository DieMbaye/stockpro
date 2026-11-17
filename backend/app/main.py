from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app import models  # noqa: F401  (pour que SQLAlchemy connaisse nos tables)
from app.database import Base, engine
from app.routers import mouvements, produits, tableau_de_bord
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="StockPro API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(produits.router)
app.include_router(mouvements.router)
app.include_router(tableau_de_bord.router)
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API StockPro"}


@app.get("/health")
def health():
    try:
        with engine.connect() as connexion:
            connexion.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "indisponible"},
        )