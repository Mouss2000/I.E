# Project Memory & Progress Log
*Soutenance Projet Innov - Cabinet 2.0*

## Architecture Générale
- **Backend** : Python / Django / Django REST Framework
- **Base de données** : SQLite (Configurée pour être portable avec PyInstaller)
- **Frontend** : React.js (Vite) / Tailwind CSS v4 / Lucide-React
- **Serveur de Production** : Waitress (embarqué dans l'exécutable)
- **Design System** : Dark Mode, Glassmorphism (`bg-[#0d0914]`, `bg-white/5`), Enterprise SaaS Layout.
- **Repo GitHub** : `https://github.com/Mouss2000/I.E.git` (branche `main`)
- **Venv** : `Soutenance/Projet Innov/venv/`
- **Python venv** : `venv/Scripts/python.exe`

## Ce qui a été accompli

### 1. Développement Backend (API Django)
- Création du projet `cabinet_backend` et de l'app `api`.
- Création du Modèle `Prescription` :
  - `patient_ref` (Anonymisation CNDP/Loi 09-08)
  - `tooth_number`, `shade`, `material`
  - `is_fast_track` (Option de livraison express)
  - `total_price` (Devis calculé)
  - `estimated_delivery_date`
  - `disinfected` (Verrou Sanitaire)
  - `status` (RECU, PROD)
- Création du Serializer avec validation stricte (le POST est rejeté si `disinfected=False`).
- Configuration de `settings.py` (CORS open pour dev, configuration DB pour production portable).

### 2. Développement Frontend (Interface React)
- Création du projet `cabinet_frontend` avec Vite.
- Résolution du problème d'intégration Tailwind v4 avec PostCSS.
- **État d'Authentification (Mock)** : Écran de connexion plein écran exigeant un nom d'utilisateur, qui est ensuite affiché dynamiquement dans toute l'application.
- **Layout Enterprise SaaS** : Sidebar (logo + info user + rôle) + Main Content Area + Header Bar.
- **Portail Dentiste** :
  - Odontogram interactif (sélection de dent par numéro FDI).
  - Guide VITA (Lightbox clinique `shade-guide.png`).
  - Grille CSS de 5 matériaux : Zircone, E-Max, Céramo-Métal, 100% Métal, Provisoire Résine.
  - Calcul de devis automatique par matériau.
  - Badge dynamique "Fast-Track".
  - Liste des commandes avec statuts colorés.

### 3. Packaging & Déploiement Standalone (PyInstaller)
- Build de production Vite (`npm run build`) intégré dans Django (`frontend_build`).
- Modification des `urls.py` pour forcer le serveur WSGI à distribuer les assets statiques et le `index.html`.
- Modification de `settings.py` pour que `db.sqlite3` écrive toujours dans le dossier de l'exécutable (`RUNTIME_BASE`), même après décompression temporaire de PyInstaller (`sys._MEIPASS`).
- Création du script `run_server.py` qui lance Waitress (production WSGI), joue les migrations manquantes, et ouvre automatiquement le navigateur web.
- Génération d'un `.exe` standalone avec PyInstaller (avec la console visible pour permettre l'arrêt du serveur).
- Zippage final de l'application dans `Cabinet2_App.zip`.

### 4. Mise à Jour Workflow 3 Portails (Dentiste, Labo, Coursier)
- **Backend API** :
  - Ajout des champs `dentist_name` et `delivery_date` au modèle `Prescription`.
  - Extension des statuts : `EN_ATTENTE`, `EN_PRODUCTION`, `PRET_EXPEDITION`, `EN_ROUTE`, `LIVRE`.
  - Passage sur `ModelViewSet` (CRUD complet) et activation du `PATCH` via CORS.
- **Frontend UI (App.jsx Rewrite)** :
  - Écran de connexion role-based (Dentiste, Prothésiste, Livreur).
  - **Portail Dentiste** : Intégration d'un Lightbox Clinique (`shade-guide.png`), grille CSS de 5 matériaux (Zircone, E-Max, Céramo-Métal, 100% Métal, Provisoire Résine) avec calcul des prix, et badge dynamique "Fast-Track".
  - **Portail Labo** : Kanban interactif pour gérer l'acceptation et la production.
  - **Portail Coursier** : Interface liste mobile-friendly pour les statuts `EN_ROUTE` et `LIVRE`.
  - **Branding** : Intégration du logo personnalisé `logo.png` (effet néon glassmorphism).
- **Packaging Final** : Re-build complet via Vite, synchronisation avec le `frontend_build` de Django, génération d'un nouvel exécutable via PyInstaller, et zippage dans `cabinet_backend/dist/Cabinet2_App.zip`. Nettoyage des artefacts de build redondants.

### 5. Intégration Métier Prothésiste CFAO & Flux Financier Marocain (2026-10-20)
- **Backend API (Django REST)** :
  - Mise à jour du modèle `Prescription` :
    - `impression_type` (`PHYSIQUE`, `NUMERIQUE`).
    - `stl_file_name` (nom du fichier numérique téléversé).
    - Pipeline CFAO prothésiste : `A_CONFIRMER`, `SALLE_CAO`, `USINAGE_CNC`, `FRITTAGE_9H`, `CONTROLE_QUALITE`, `PRET_EXPEDITION`, `EN_ROUTE`, `LIVRE`.
    - Remplacement de `payment_status` par `billing_stage` (`COMMANDE`, `SITUATION`, `FACTURE`).
  - Serializer mis à jour avec permissions en écriture via `PATCH`.
  - Application de la migration `0005_remove_prescription_payment_status_and_more.py`.
  - Réinitialisation propre de la base SQLite (`db.sqlite3`) avec migrations rejouées.
- **Frontend UI (React & Tailwind)** :
  - **Portail Dentiste** :
    - Sélecteur de type d'empreinte (Physique vs Numérique .STL).
    - Zone de drop glassmorphism pour fichiers `.stl`/`.ply`.
    - Calcul de l'urgence 24h-48h (+30% sur le prix de base, remplace +200 MAD flat).
    - Affichage synchronisé des nouveaux statuts CFAO dans la liste des commandes.
  - **Portail Labo (Onglet Commandes)** :
    - Pipeline de production CFAO en 5 étapes séquentielles avec progression `PATCH`.
    - Gestion sécurisée de la date de livraison estimée sur `A_CONFIRMER`.
    - Badges techniques par étape (Exocad, fraisage 5-axes, frittage 1500°C 9h, contrôle/glaçage).
  - **Portail Labo (Onglet Facturation)** :
    - Cycle financier marocain en 3 étapes : Bons de Commande -> Relevé de Situation mensuel (cumul MAD en temps réel & validation groupée) -> Facturation Définitive (téléchargement PDF).
- **Packaging & Déploiement Standalone** :
  - Rebuild des assets de production Vite (`npm run build`).
  - Copie dans `cabinet_backend/frontend_build`.
  - Recompilation binaire via PyInstaller (`Cabinet2.spec`).
  - Archivage final compressé dans `cabinet_backend/dist/Cabinet2_App.zip` (~25.5 Mo).
- **Git** : Commit `ccb5121` pushed to `origin/main`. `memory.md` retiré du repo (`70bfe23`).

### 6. Routage Two-Way Coursier & Drag & Drop HTML5 (2026-10-21)
- **Backend API (Django REST)** :
  - Nouveaux statuts de pré-labo : `ATTENTE_RAMASSAGE`, `EN_ROUTE_LABO`.
  - Renommage `EN_ROUTE` -> `EN_ROUTE_CABINET`.
  - Logique de routage intelligent dans `Prescription.save()` :
    - `PHYSIQUE` -> statut initial `ATTENTE_RAMASSAGE`.
    - `NUMERIQUE` -> statut initial `A_CONFIRMER` (bypass coursier).
  - Migration `0006_alter_prescription_status.py` générée et appliquée.
- **Frontend UI (React Drag & Drop & Two-Way Logistics)** :
  - **Portail Labo (CFAO)** :
    - Cartes de commande `draggable={true}` avec feedback visuel cursor/scale.
    - Conteneurs d'étapes avec `onDragOver` et `onDrop`.
    - Chaîne séquentielle stricte : `A_CONFIRMER` -> `SALLE_CAO` -> `USINAGE_CNC` -> `FRITTAGE_9H` -> `CONTROLE_QUALITE` -> `PRET_EXPEDITION`.
    - Highlight réactif de l'étape suivante autorisée (`ring-2 ring-emerald-500/50 bg-emerald-900/10`).
    - Validation stricte `index + 1` avant déclenchement du `PATCH`.
  - **Portail Labo (Facturation)** :
    - DnD identique sur la chaîne comptable : `COMMANDE` -> `SITUATION` -> `FACTURE`.
    - Highlight vert de l'étape suivante pendant le glisser-déposer.
  - **Portail Coursier (Two-Way Routing)** :
    - **Section A (Phase 1 : Ramassages au Cabinet)** : Filtre `ATTENTE_RAMASSAGE || EN_ROUTE_LABO`. Rendu conditionnel strict : bouton orange "Scanner & Récupérer" si `ATTENTE_RAMASSAGE`, bouton bleu "Déposer au Labo" si `EN_ROUTE_LABO`.
    - **Section B (Phase 2 : Livraisons au Cabinet)** : Filtre `PRET_EXPEDITION || EN_ROUTE_CABINET`. Rendu conditionnel strict : bouton violet "Scanner & Récupérer" si `PRET_EXPEDITION`, bouton vert "Valider PIN & Livrer" si `EN_ROUTE_CABINET`.
  - **Correction du routage initial (Backend + Frontend)** :
    - `PrescriptionViewSet.perform_create` intercepte `impression_type` : force `ATTENTE_RAMASSAGE` si `PHYSIQUE`, `A_CONFIRMER` si `NUMERIQUE`.
    - `handleSubmit` dans le formulaire dentiste transmet explicitement `impression_type: formData.impression_type`.
  - **Packaging Standalone Exécutable** :
    - Rebuild des assets de production Vite (`npm run build`).
    - Synchronisation dans `cabinet_backend/frontend_build`.
    - Recompilation complète PyInstaller (`Cabinet2.spec`).
    - Archive standalone finale mise à jour : [`cabinet_backend/dist/Cabinet2_App.zip`](file:///C:/Users/SetupGame/OneDrive/Desktop/New%20folder/Soutenance/Projet%20Innov/cabinet_backend/dist/Cabinet2_App.zip) (25.5 Mo, 10/21/2026).

## Référence Rapide

### Commandes Dev
```powershell
# Backend dev server
cd "Soutenance/Projet Innov/cabinet_backend"
& "../../venv/Scripts/python.exe" manage.py runserver

# Frontend dev server
cd "Soutenance/Projet Innov/cabinet_frontend"
npm run dev

# Migrations
& "../../venv/Scripts/python.exe" manage.py makemigrations api
& "../../venv/Scripts/python.exe" manage.py migrate

# DB reset
Remove-Item "cabinet_backend/db.sqlite3"
& "venv/Scripts/python.exe" manage.py migrate
```

### Pipeline Build Production
```powershell
# 1. Build frontend
cd cabinet_frontend && npm run build

# 2. Sync to Django
Remove-Item -Recurse -Force cabinet_backend/frontend_build
Copy-Item -Recurse cabinet_frontend/dist cabinet_backend/frontend_build

# 3. PyInstaller
cd cabinet_backend
& "../venv/Scripts/python.exe" -m PyInstaller Cabinet2.spec --noconfirm --clean

# 4. Zip
Compress-Archive -Path "dist/Cabinet2/*" -DestinationPath "dist/Cabinet2_App.zip" -Force
```

### Fichiers Clés
| Fichier | Rôle |
|---|---|
| `cabinet_backend/api/models.py` | Modèle Prescription (8 statuts CFAO, billing_stage, impression_type) |
| `cabinet_backend/api/serializers.py` | Serializer avec Verrou Sanitaire + PATCH unlock |
| `cabinet_backend/api/views.py` | ModelViewSet CRUD |
| `cabinet_backend/run_server.py` | Waitress launcher + auto-migrate + browser open |
| `cabinet_backend/Cabinet2.spec` | PyInstaller spec (frontend_build embedded) |
| `cabinet_backend/cabinet_backend/settings.py` | RUNTIME_BASE portable DB config |
| `cabinet_frontend/src/App.jsx` | Monolithique React (Login + 3 portails) |
| `cabinet_frontend/vite.config.js` | `base: '/static/'` pour Django serving |
