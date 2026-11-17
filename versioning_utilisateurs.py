
import os
import io
import json
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

chemin = "exercice/year=2026/month=11/day=17/profil_1.json"

# Modification du hobby du premier utilisateur
profil_modifie = {
    "prenom": "Youssef",
    "ville": "Paris",
    "hobby": "Natation",
    "age": 25
}

contenu = json.dumps(profil_modifie).encode("utf-8")

# Upload au même chemin
client.put_object(
    "bronze",
    chemin,
    io.BytesIO(contenu),
    length=len(contenu),
    content_type="application/json"
)

print("Profil modifié et réimporté au même chemin.")

# Liste des versions
print("\n=== VERSIONS DU PROFIL 1 ===")

for objet in client.list_objects(
    "bronze",
    prefix=chemin,
    recursive=True,
    include_version=True
):
    if objet.object_name == chemin and not objet.is_delete_marker:
        print(f"Version ID : {objet.version_id}")

        response = client.get_object(
            "bronze",
            chemin,
            version_id=objet.version_id
        )

        try:
            profil = json.loads(response.read())
            print(f"Hobby : {profil['hobby']}")
        finally:
            response.close()
            response.release_conn()

        print("---")
