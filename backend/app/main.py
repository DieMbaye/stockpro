from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app import models  # noqa: F401  (pour que SQLAlchemy connaisse nos tables)
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="StockPro API", lifespan=lifespan)


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