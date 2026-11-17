from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
from io import BytesIO
import json

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Nouvelle version du même fichier
donnees = {
    "source": "demonstration",
    "date": "2026-11-17",
    "message": "Deuxième version du fichier !"
}

contenu = json.dumps(donnees, indent=2).encode("utf-8")

resultat = client.put_object(
    "bronze",
    "demo/premier_fichier.json",
    BytesIO(contenu),
    len(contenu),
    content_type="application/json"
)

print("Nouvelle version enregistrée")
print("Version ID :", resultat.version_id)

# Afficher les versions existantes
print("\nVersions du fichier :")

for obj in client.list_objects(
    "bronze",
    prefix="demo/premier_fichier.json",
    include_version=True
):
    print("Version :", obj.version_id)
