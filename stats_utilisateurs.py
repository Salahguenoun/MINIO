
import os
import io
import json
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

# Lecture du fichier Parquet depuis Silver
response = client.get_object(
    "silver",
    "exercice/utilisateurs_propres.parquet"
)

try:
    df = pd.read_parquet(io.BytesIO(response.read()))
finally:
    response.close()
    response.release_conn()

print("=== DONNÉES SILVER ===")
print(df)

# Agrégation : nombre d'utilisateurs par ville
stats = (
    df.groupby("ville")
    .size()
    .reset_index(name="nombre_utilisateurs")
)

print("\n=== STATISTIQUES PAR VILLE ===")
print(stats)

# Conversion en JSON
resultat = stats.to_dict(orient="records")

contenu = json.dumps(
    resultat,
    indent=2,
    ensure_ascii=False
).encode("utf-8")

# Enregistrement dans Gold
client.put_object(
    bucket_name="gold",
    object_name="exercice/stats_villes.json",
    data=io.BytesIO(contenu),
    length=len(contenu),
    content_type="application/json"
)

print("\nFichier créé : gold/exercice/stats_villes.json")
print(json.dumps(resultat, indent=2, ensure_ascii=False))
