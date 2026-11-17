
import os
from datetime import timedelta
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

# Générer une URL pré-signée valable 1 heure
url = client.presigned_get_object(
    bucket_name="gold",
    object_name="exercice/stats_villes.json",
    expires=timedelta(hours=1)
)

print("=== URL PRÉ-SIGNÉE ===")
print(url)
print("\nDurée de validité : 1 heure")
