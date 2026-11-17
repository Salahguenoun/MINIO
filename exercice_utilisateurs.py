
import os
import json
import io
from datetime import datetime
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False,
    region="us-east-1"
)

# Liste de 3 profils utilisateurs
utilisateurs = [
    {"prenom": "Youssef", "ville": "Paris", "hobby": "Football", "age": 25},
    {"prenom": "Sara", "ville": "Lyon", "hobby": "Lecture", "age": 17},
    {"prenom": "Amine", "ville": "Paris", "hobby": "Musique", "age": 30}
]

# Partitionnement selon la date du jour
date = datetime.now()
dossier = (
    f"exercice/year={date.year}/"
    f"month={date.month:02d}/"
    f"day={date.day:02d}"
)

# Upload individuel des profils
for i, utilisateur in enumerate(utilisateurs, start=1):
    chemin = f"{dossier}/profil_{i}.json"

    contenu = json.dumps(
        utilisateur,
        ensure_ascii=False
    ).encode("utf-8")

    client.put_object(
        "bronze",
        chemin,
        io.BytesIO(contenu),
        length=len(contenu),
        content_type="application/json"
    )

    print(f"Upload réussi : bronze/{chemin}")

print("\n3 profils enregistrés dans Bronze.")
