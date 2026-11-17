# TP Data Lake — Docker, MinIO et Python

## Objectif

Mise en place d'un Data Lake avec Docker, MinIO et Python, organisé en trois couches :

- **Bronze** : stockage des données brutes avec versioning.
- **Silver** : nettoyage, transformation et stockage au format Parquet.
- **Gold** : agrégations et résultats au format JSON.

## Technologies

Docker, MinIO, Python, Pandas, PyArrow et MinIO Client (mc).

## Installation

1. Installer les dépendances Python :

   pip install -r requirements.txt

2. Copier `.env.example` vers `.env` et renseigner les identifiants.

3. Démarrer MinIO :

   docker compose up -d

4. Initialiser les buckets et le versioning :

   python minio_tp.py

MinIO API : http://localhost:9000

Console MinIO : http://localhost:9001

## Partie 1 — Infrastructure MinIO

- Déploiement de MinIO avec Docker Compose.
- Création des buckets `bronze`, `silver` et `gold`.
- Activation du versioning sur Bronze.
- Upload d'un premier fichier et vérification du versioning.

Scripts :

- `minio_tp.py`
- `upload_bronze.py`
- `test_versioning.py`

## Partie 2 — Traitement des sinistres d'assurance

### Bronze

Importation de trois dossiers de sinistres contenant chacun quatre fichiers : CSV, image, audio et PDF.

Scripts :

- `import_sinistre.py`
- `generer_sinistres.py`

Résultat : 12 fichiers archivés dans Bronze.

### Silver

Extraction des informations métier et des métadonnées techniques, puis consolidation avec Pandas.

Script : `extraire_sinistres.py`

Fichier généré :

`silver/sinistres/catalogue_global.parquet`

Résultat : 12 lignes et 10 colonnes.

### Gold

Agrégation des sinistres par type.

Script : `rapport_gold.py`

Fichier généré :

`gold/reporting/synthese_sinistres.json`

| Type de sinistre | Fichiers | Montant estimé |
|---|---:|---:|
| Accident voiture | 4 | 1 450,50 € |
| Dégât des eaux | 4 | 3 200,00 € |
| Vol effraction | 4 | 5 800,00 € |
| **Total** | **12** | **10 450,50 €** |

### Sécurité IAM

- Création de la politique `lecture_gold` définie dans `policy_gold.json`.
- Création de l'utilisateur `analyste_junior`.
- Attribution des droits `s3:ListBucket` et `s3:GetObject` uniquement sur Gold.

Script de vérification : `test_iam.py`

Résultats :
- Lecture Gold : autorisée.
- Lecture Bronze : refusée (`AccessDenied`).

La politique et l'utilisateur IAM sont configurés avec MinIO Client (`mc`).

## Partie 3 — Profils utilisateurs

### Bronze : ingestion et versioning

Création de trois profils JSON contenant le prénom, la ville, le hobby et l'âge.

Partitionnement :

`bronze/exercice/year=2026/month=11/day=17/`

Scripts :

- `exercice_utilisateurs.py`
- `versioning_utilisateurs.py`

Le hobby du premier utilisateur a été modifié de Football à Natation. Les deux versions du fichier ont été conservées dans Bronze.

### Silver : nettoyage

Script : `nettoyer_utilisateurs.py`

Transformations :
- Conversion des prénoms en majuscules.
- Exclusion des utilisateurs de moins de 18 ans.
- Ajout de la colonne `date_traitement`.
- Conversion en Parquet.

Fichier généré :

`silver/exercice/utilisateurs_propres.parquet`

Métadonnées personnalisées :
- `auteur` : `data_engineer`
- `source` : `bronze`

Résultat : deux utilisateurs majeurs conservés.

### Gold : statistiques

Script : `stats_utilisateurs.py`

Agrégation : nombre d'utilisateurs par ville.

Fichier généré :

`gold/exercice/stats_villes.json`

Résultat :

| Ville | Nombre d'utilisateurs |
|---|---:|
| Paris | 2 |

### URL pré-signée

Script : `presigned_url.py`

Génération d'une URL pré-signée valable une heure pour télécharger le fichier Gold sans fournir les identifiants MinIO.

Test réalisé avec `curl` : **HTTP 200**.

L'URL utilisant `localhost` est accessible depuis l'environnement où MinIO est exécuté. Un accès externe nécessite une adresse réseau accessible par l'analyste.

## Sécurité

Les identifiants sont stockés dans le fichier `.env`, exclu de Git grâce à `.gitignore`.

Le répertoire `minio_data/` est également exclu du dépôt GitHub.
