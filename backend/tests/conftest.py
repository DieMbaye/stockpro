import os

import pytest
from dotenv import dotenv_values

# 1. Trouver l'adresse de la base de TEST
url_test = os.getenv("TEST_DATABASE_URL") or dotenv_values(".env").get("TEST_DATABASE_URL")
if not url_test:
    raise RuntimeError("TEST_DATABASE_URL manquant (dans .env ou en variable d'environnement)")

# 2. Sécurité : refuser de lancer les tests sur une base qui n'est pas une base de test
if "test" not in url_test:
    raise RuntimeError("Par sécurité, TEST_DATABASE_URL doit pointer vers une base de test")

# 3. Faire utiliser la base de test par toute l'application
os.environ["DATABASE_URL"] = url_test

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c  
        
        
                   