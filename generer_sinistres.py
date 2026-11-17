from dotenv import load_dotenv
load_dotenv()
import os

from pathlib import Path
import csv
import wave

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from minio import Minio

# Connexion à MinIO
client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

# Deux dossiers de sinistres à générer
sinistres = [
    {
        "id": "SIN-20xx-002",
        "type": "degat des eaux",
        "client": "Client B",
        "montant": 3200,
        "statut": "En cours"
    },
    {
        "id": "SIN-2026-003",
        "type": "vol effraction",
        "client": "Client C",
        "montant": 5800,
        "statut": "En cours"
    }
]

for sinistre in sinistres:
    identifiant = sinistre["id"]
    dossier = Path("fichiers_source") / identifiant
    dossier.mkdir(parents=True, exist_ok=True)

    # 1. Fichier CSV
    with open(dossier / "infos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_sinistre", "type_sinistre", "client",
            "montant_estime", "statut"
        ])
        writer.writerow([
            identifiant,
            sinistre["type"],
            sinistre["client"],
            sinistre["montant"],
            sinistre["statut"]
        ])

    # 2. Image PNG
    image = Image.new("RGB", (600, 300), "white")
    dessin = ImageDraw.Draw(image)
    dessin.text((30, 50), identifiant, fill="black")
    dessin.text((30, 100), sinistre["type"], fill="black")
    image.save(dossier / "image.png")

    # 3. Fichier audio WAV
    with wave.open(str(dossier / "audio.wav"), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\x00\x00" * 8000)

    # 4. Fichier PDF
    pdf = canvas.Canvas(str(dossier / "constat.pdf"))
    pdf.drawString(50, 750, f"Sinistre : {identifiant}")
    pdf.drawString(50, 720, f"Type : {sinistre['type']}")
    pdf.drawString(50, 690, f"Montant estime : {sinistre['montant']} EUR")
    pdf.save()

    # Upload des 4 fichiers dans Bronze
    annee = identifiant.split("-")[1]
    chemin = f"sinistres/{annee}/mm/jj/{identifiant}/"

    fichiers = {
        "infos.csv": "text/csv",
        "image.png": "image/png",
        "audio.wav": "audio/wav",
        "constat.pdf": "application/pdf"
    }

    for nom, mime in fichiers.items():
        client.fput_object(
            "bronze",
            chemin + nom,
            str(dossier / nom),
            content_type=mime
        )

    print(f"{identifiant} : 4 fichiers envoyés dans Bronze")

print("Importation terminée !")
