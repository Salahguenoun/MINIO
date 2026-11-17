from dotenv import load_dotenv
load_dotenv()
import os

from minio import Minio
import pandas as pd
import io
import unicodedata

client = Minio(
    "localhost:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False
)

donnees = []

# Parcourir tous les fichiers de Bronze
objets = list(client.list_objects(
    "bronze",
    prefix="sinistres/",
    recursive=True
))

# Lire les informations métier des trois sinistres
for obj in objets:
    if obj.object_name.endswith("/infos.csv"):
        reponse = client.get_object("bronze", obj.object_name)

        try:
            df = pd.read_csv(io.BytesIO(reponse.read()))
        finally:
            reponse.close()
            reponse.release_conn()

        # Harmoniser les noms des colonnes
        def nettoyer_colonne(nom):
            nom = nom.strip().lower().replace(" ", "_")
            nom = unicodedata.normalize("NFKD", nom)
            return "".join(
                c for c in nom if not unicodedata.combining(c)
            )

        df.columns = [nettoyer_colonne(col) for col in df.columns]

        # Corriger le nom de la colonne
        df = df.rename(columns={"satus": "statut"})

        # Récupérer les informations métier
        for _, ligne in df.iterrows():
            donnees.append({
                "dossier": obj.object_name.rsplit("/", 1)[0],
                "id_sinistre": ligne["id_sinistre"],
                "type_sinistre": ligne["type_sinistre"],
                "client": ligne["client"],
                "montant_estime": ligne["montant_estime"],
                "statut": ligne["statut"]
            })

# Afficher les données métier
df_metier = pd.DataFrame(donnees)

print("=== DONNÉES MÉTIER ===")
print(df_metier.to_string(index=False))

# Extraire les métadonnées techniques
metadonnees = []

for obj in objets:
    info = client.stat_object("bronze", obj.object_name)

    metadonnees.append({
        "dossier": obj.object_name.rsplit("/", 1)[0],
        "nom_fichier": obj.object_name.split("/")[-1],
        "chemin_s3": f"s3://bronze/{obj.object_name}",
        "type_mime": info.content_type,
        "taille_octets": info.size
    })

df_technique = pd.DataFrame(metadonnees)

print("\n=== MÉTADONNÉES TECHNIQUES ===")
print(df_technique.to_string(index=False))

print("\nNombre de sinistres :", len(df_metier))
print("Nombre de fichiers :", len(df_technique))


# Fusionner les données métier et techniques
catalogue = pd.merge(
    df_technique,
    df_metier,
    on="dossier",
    how="left"
)

# Convertir le DataFrame en Parquet
buffer = io.BytesIO()
catalogue.to_parquet(buffer, index=False)
buffer.seek(0)

# Envoyer le catalogue dans Silver
client.put_object(
    bucket_name="silver",
    object_name="sinistres/catalogue_global.parquet",
    data=buffer,
    length=buffer.getbuffer().nbytes,
    content_type="application/vnd.apache.parquet"
)

print("\n=== CATALOGUE SILVER ===")
print("Nombre de lignes :", len(catalogue))
print("Nombre de colonnes :", len(catalogue.columns))
print("Fichier créé : silver/sinistres/catalogue_global.parquet")
