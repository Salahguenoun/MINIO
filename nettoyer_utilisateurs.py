
import os
import io
import json
from datetime import datetime
import pandas as pd
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

# Dossier contenant les profils JSON
dossier = "exercice/year=2026/month=11/day=17/"

# Lecture des fichiers JSON dans Bronze
profils = []

for objet in client.list_objects(
    "bronze",
    prefix=dossier,
    recursive=True
):
    if objet.object_name.endswith(".json"):
        response = client.get_object(
            "bronze",
            objet.object_name
        )

        try:
            profil = json.loads(response.read())
            profils.append(profil)
        finally:
            response.close()
            response.release_conn()

df = pd.DataFrame(profils)

print("=== DONNÉES BRUTES ===")
print(df)

# Nettoyage
df["prenom"] = df["prenom"].str.upper()
df = df[df["age"] >= 18].copy()
df["date_traitement"] = datetime.now().date().isoformat()

print("\n=== DONNÉES NETTOYÉES ===")
print(df)

# Conversion au format Parquet
buffer = io.BytesIO()
df.to_parquet(buffer, engine="pyarrow", index=False)
contenu = buffer.getvalue()

# Upload dans Silver avec métadonnées personnalisées
client.put_object(
    bucket_name="silver",
    object_name="exercice/utilisateurs_propres.parquet",
    data=io.BytesIO(contenu),
    length=len(contenu),
    content_type="application/octet-stream",
    metadata={
        "auteur": "data_engineer",
        "source": "bronze"
    }
)

print("\nFichier créé : silver/exercice/utilisateurs_propres.parquet")

# Vérification des métadonnées
infos = client.stat_object(
    "silver",
    "exercice/utilisateurs_propres.parquet"
)

print("Métadonnées :", infos.metadata)
