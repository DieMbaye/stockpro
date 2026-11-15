from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import engine

app = FastAPI(title="StockPro API")


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
