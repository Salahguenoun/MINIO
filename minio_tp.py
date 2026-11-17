from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
from minio.versioningconfig import VersioningConfig, ENABLED

# Connexion à MinIO
client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Afficher les buckets existants
print("Buckets existants :")
for bucket in client.list_buckets():
    print("-", bucket.name)

# Créer les trois buckets
buckets_a_creer = ["bronze", "silver", "gold"]

for bucket_name in buckets_a_creer:
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' créé")
    else:
        print(f"Bucket '{bucket_name}' existe déjà")

# Activer le versioning sur Bronze
client.set_bucket_versioning(
    "bronze",
    VersioningConfig(ENABLED)
)

# Vérifier le versioning
config = client.get_bucket_versioning("bronze")
print("Versioning Bronze :", config.status)
