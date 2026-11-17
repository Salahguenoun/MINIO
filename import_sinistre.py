from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

chemin = "sinistres/20xx/mm/jj/SIN-20xx-042/"

fichiers = {
    "infos.csv": ("fichiers_source/infos.csv", "text/csv"),
    "impact-accident-voiture.jpg": (
        "fichiers_source/impact-accident-voiture.jpg",
        "image/jpeg"
    ),
    "temoignage_audio.wav": (
        "fichiers_source/temoignage_audio.wav",
        "audio/wav"
    ),
    "constat.pdf": (
        "fichiers_source/constat.pdf",
        "application/pdf"
    )
}

for nom, (fichier, mime) in fichiers.items():
    client.fput_object(
        "bronze",
        chemin + nom,
        fichier,
        content_type=mime
    )
    print(f"Fichier envoyé : {nom}")

print("Importation terminée !")
