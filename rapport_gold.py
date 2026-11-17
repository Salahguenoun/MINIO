from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
import pandas as pd
import io
import json

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Lire le catalogue Parquet depuis Silver
response = client.get_object(
    "silver",
    "sinistres/catalogue_global.parquet"
)

try:
    df = pd.read_parquet(io.BytesIO(response.read()))
finally:
    response.close()
    response.release_conn()

# Calculer la synthèse par type de sinistre
# Chaque sinistre apparaît plusieurs fois (une fois par fichier)
synthese = df.groupby("type_sinistre").agg(
    nombre_fichiers=("nom_fichier", "count"),
    montant_total_estime=("montant_estime",
                          lambda x: x.groupby(df.loc[x.index, "id_sinistre"]).first().sum())
).reset_index()

# Convertir en JSON
resultat = synthese.to_dict(orient="records")
contenu = json.dumps(resultat, indent=2, ensure_ascii=False).encode("utf-8")

# Envoyer dans Gold
client.put_object(
    bucket_name="gold",
    object_name="reporting/synthese_sinistres.json",
    data=io.BytesIO(contenu),
    length=len(contenu),
    content_type="application/json"
)

print("=== RAPPORT GOLD ===")
print(json.dumps(resultat, indent=2, ensure_ascii=False))
print("\nFichier créé : gold/reporting/synthese_sinistres.json")
