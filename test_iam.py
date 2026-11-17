from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
from minio.error import S3Error

# Connexion avec l'utilisateur analyste_junior
client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_JUNIOR_USER"),
    secret_key=os.getenv("MINIO_JUNIOR_PASSWORD"),
    secure=False,
    region="us-east-1"
)

# Test 1 : lecture autorisée sur Gold
try:
    response = client.get_object(
        "gold",
        "reporting/synthese_sinistres.json"
    )
    try:
        print("GOLD : lecture autorisée")
        print(response.read().decode("utf-8"))
    finally:
        response.close()
        response.release_conn()

except S3Error as e:
    print("GOLD : erreur", e.code)

# Test 2 : lecture interdite sur Bronze
try:
    response = client.get_object(
        "bronze",
        "sinistres/20xx/mm/jj/SIN-20xx-042/constat.pdf"
    )
    try:
        response.read()
        print("BRONZE : lecture autorisée (ERREUR)")
    finally:
        response.close()
        response.release_conn()

except S3Error as e:
    print("BRONZE :", e.code)
