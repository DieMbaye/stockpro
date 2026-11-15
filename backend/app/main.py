from fastapi import FastAPI

app = FastAPI(title="StockPro API")


@app.get("/")
def accueil():
    return {"message": "Bienvenue sur l'API StockPro"}


@app.get("/health")
def health():
    return {"status": "ok"}
