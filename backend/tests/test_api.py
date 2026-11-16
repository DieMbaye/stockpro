def creer_produit(client, nom="Cahier", prix=500, seuil_alerte=10):
    reponse = client.post(
        "/produits", json={"nom": nom, "prix": prix, "seuil_alerte": seuil_alerte}
    )
    return reponse.json()


def mouvement(client, produit_id, type_, quantite):
    return client.post(
        "/mouvements",
        json={"produit_id": produit_id, "type": type_, "quantite": quantite},
    )


def test_health(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.json()["database"] == "ok"


def test_creer_produit_commence_a_zero(client):
    reponse = client.post("/produits", json={"nom": "Cahier", "prix": 500})
    assert reponse.status_code == 201
    assert reponse.json()["quantite"] == 0


def test_doublon_refuse(client):
    creer_produit(client, nom="Cahier")
    reponse = client.post("/produits", json={"nom": "Cahier", "prix": 500})
    assert reponse.status_code == 409


def test_prix_negatif_refuse(client):
    reponse = client.post("/produits", json={"nom": "Cahier", "prix": -100})
    assert reponse.status_code == 422


def test_entree_puis_sortie(client):
    produit = creer_produit(client)
    mouvement(client, produit["id"], "entree", 50)
    mouvement(client, produit["id"], "sortie", 10)
    reponse = client.get(f"/produits/{produit['id']}")
    assert reponse.json()["quantite"] == 40


def test_stock_insuffisant(client):
    produit = creer_produit(client)
    mouvement(client, produit["id"], "entree", 5)
    reponse = mouvement(client, produit["id"], "sortie", 10)
    assert reponse.status_code == 400


def test_suppression_refusee_si_historique(client):
    produit = creer_produit(client)
    mouvement(client, produit["id"], "entree", 5)
    reponse = client.delete(f"/produits/{produit['id']}")
    assert reponse.status_code == 409


def test_alerte_et_tableau_de_bord(client):
    stylo = creer_produit(client, nom="Stylo", prix=150, seuil_alerte=20)
    mouvement(client, stylo["id"], "entree", 3)

    reponse = client.get("/tableau-de-bord")
    donnees = reponse.json()
    assert donnees["nombre_produits"] == 1
    assert donnees["valeur_totale_stock"] == 450
    assert donnees["nombre_alertes"] == 1
    assert donnees["produits_en_alerte"][0]["en_alerte"] is True