from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
import json
from io import BytesIO

# Connexion à MinIO
client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Données exemple
donnees_exemple = {
    "source": "demonstration",
    "date": "2026-11-17",
    "message": "Premier fichier dans le Data Lake !"
}

# Convertir en JSON
json_data = json.dumps(donnees_exemple, indent=2)
json_bytes = json_data.encode("utf-8")

# Envoyer le fichier dans Bronze
client.put_object(
    bucket_name="bronze",
    object_name="demo/premier_fichier.json",
    data=BytesIO(json_bytes),
    length=len(json_bytes),
    content_type="application/json"
)

print("Fichier envoyé dans Bronze")

# Lire le fichier depuis Bronze
response = client.get_object(
    "bronze",
    "demo/premier_fichier.json"
)

contenu = response.read().decode("utf-8")
response.close()
response.release_conn()

print("Contenu du fichier :")
print(contenu)
