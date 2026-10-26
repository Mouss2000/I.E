# Project Memory & Progress Log

## Réorganisation overview / gestion des commandes (2026-10-26)

- Barre latérale du laboratoire : Menu principal, Commandes, Facturation, Configuration. L’ancien onglet Interface client est retiré.
- Menu principal informatif : Dashboard avec indicateurs issus des données et panneau d’alertes compact à droite sous les indicateurs ; Commandes avec grandes cartes (ID, client, dates, tâche, progression, problèmes, motif de pause) ; Facturation avec montants et aperçu en lecture seule.
- Gestion Commandes : deux onglets Commandes / Étapes de commandes. Deux colonnes reçues / acceptées. Acceptation persistée, clic sur une carte acceptée ouvrant son diagramme.
- Diagramme par commande : fiche déplaçable vers la prochaine étape autorisée, blocs numérotés, étapes adaptées à la méthode ; bouton de validation disponible également. Les contrôles de réception / qualité et les étapes du coursier restent appliqués.
- Pause persistante avec motif obligatoire, problèmes actuels ; avancement bloqué pendant une pause. Date d’acceptation et date de réception effective enregistrées par le serveur.
- Départ des nouvelles demandes : DEMANDE_RECUE, acceptation, puis ANALYSE_DEMANDE. Migrations 0011 / 0012 : nouvelles données et reprise des commandes déjà en cours comme acceptées.
- Facturation opérationnelle déplacée dans sa propre rubrique latérale ; vue générale conservée dans le menu principal.
- Validation : 12 tests Django passent. Test navigateur vérifiant aperçu sans actions, acceptation, colonnes, diagramme, deux glisser-déposer, motif/problèmes persistants et facturation séparée. Données QA supprimées.

## Parcours de production par méthode (2026-10-26)

- Nouveau composant `ProductionWorkflow.jsx` dans Interface client, remplaçant le pipeline CNC unique. Vues par phase, recherche, fiche par commande, étapes détaillées, notes et historique horodaté.
- Départ des nouvelles commandes : analyse de la demande ; empreintes physiques passent ensuite par ramassage / coursier, les numériques passent directement à la réception. Réception → contrôle du dossier → planification.
- Choix à la planification : CFAO / usinage CNC, impression 3D ou fabrication conventionnelle ; date de livraison requise.
- CFAO : CAO → préparation FAO → usinage → traitement thermique uniquement si sélectionné (frittage, cristallisation ou cuisson) → finition.
- Impression 3D : CAO → préparation plateau/supports → impression → lavage/séchage → post-polymérisation → finition.
- Conventionnel : modèle de travail → modelage → fabrication conventionnelle → finition.
- Fin commune : contrôle qualité validé → conditionnement → prêt à expédier → coursier → livré. Aucun paramètre de temps/température n'est imposé par l'application.
- API : statuts, méthode, traitement, notes, validations et historique persistants. Les transitions non séquentielles sont rejetées côté serveur ; la méthode est verrouillée après lancement technique. Métadonnées du parcours renvoyées par le backend.
- Migrations 0009 / 0010 : les anciennes commandes conservent leur statut et leur route CFAO. Correction de la génération du PIN pour les nouvelles commandes à clé UUID.
- Validation : 10 tests Django passent, build Vite réussi, trois parcours validés de bout en bout dans le navigateur jusqu'à l'expédition ; données de test supprimées. Lint : seul avertissement préexistant de l'effet de chargement dans App.jsx.
- Référence de structuration du post-traitement 3D : https://dental.formlabs.com/post-processing/ ; les protocoles concrets restent ceux du matériau et de l'équipement choisis par le labo.

## Configuration du laboratoire (2026-10-26)

- Alertes : API `alerts/` calculée dans le schéma du labo ; stock au seuil ou en dessous, stock périmé, maintenance à J−7 ou dépassée, contrats et qualifications à J−7 ou dépassés. Dates optionnelles `contract_end_date` et `qualification_expiry_date` ajoutées au personnel (migration 0008).
- Petite notification rouge cliquable vers la section Alertes du dashboard ; chaque alerte ouvre directement sa fiche d’origine en modification dans Configuration.
- Actualisation toutes les 30 secondes, au retour dans la fenêtre et après modification des ressources. Les alertes se résolvent automatiquement lorsque leur cause est corrigée.
- Validation des alertes : 7 tests Django passent ; parcours navigateur popup → dashboard → fiche → correction vérifié pour stock, maintenance, contrat et qualifications. Données de test supprimées après vérification.

- Navigation réorganisée : boutons Menu principal et Configuration dans la barre latérale du labo. Menu principal regroupe Dashboard, Interface client (pipeline CFAO existant) et Facturation.
- Informations utilisateur / rôle / laboratoire et déconnexion déplacées dans Mon compte, en haut à droite pour tous les portails. Fermeture au clic extérieur, changement de focus ou Échap ; déconnexion efface le tenant et réinitialise la navigation.
- Vérification navigateur de la navigation et du menu compte réussie ; build Vite réussi.

- Nouvel onglet Configuration dans le portail Laboratoire : Personnel, Matériel et Stock.
- Personnel : matricule, nom, rôle, qualifications, coordonnées, suivi administratif du compte, disponibilité, horaires et date de disponibilité.
- Matériel : ID, nom, disponibilité, capacité et unité, tâches, date de disponibilité et maintenance.
- Stock : référence, article, quantité, unité, seuil d'alerte, lot, réception et péremption ; alertes de stock bas et de péremption.
- CRUD persistant via les API `staff/`, `equipment/`, `stock/`, dans le schéma du laboratoire ; migration `0007`.
- Le suivi des comptes ne crée pas d'authentification : l'écran de connexion reste une démonstration, sans application des permissions du personnel.
- Validation : 5 tests Django passent ; parcours navigateur des trois sections vérifiés (création, modification, rechargement, suppression) ; build Vite réussi. Le lint conserve uniquement les avertissements préexistants dans App.jsx.
- Environnement local : `.venv`, PostgreSQL séparé dans `C:/Users/Moham/cabinet-ie-local-postgres` (127.0.0.1:5433, utilisateur cabinet_dev, base cabinet), tenant `labo1.localhost`. Backend : définir POSTGRES_USER=cabinet_dev et POSTGRES_PORT=5433 avant `manage.py runserver 127.0.0.1:8000`. Frontend : `npm run dev -- --host 127.0.0.1 --port 5173`, URL `/static/`.
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
- **Git** : Commit `a65edce` poussé sur `origin/main` (`https://github.com/Mouss2000/I.E.git`).

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

## Tenant SaaS Upgrade Traceability (2026-10-22)

- Backend migrated from SQLite configuration to PostgreSQL with `django_tenants`; database connection values are read from `POSTGRES_*` environment variables.
- Added the `customers` app with `Client` and `Domain` tenant models and its initial migration. Configured shared/tenant apps, schema router, tenant models, and `TenantMainMiddleware`.
- Frontend added Axios tenant-aware routing using `tenant_id` from local storage and hostname routing (`{tenant}.localhost`), plus a tenant context/provider and lab label.
- Added the `caveman` workspace skill under `.github/skills/caveman/`.
- Validation: frontend `npm run build` passed; `npm run lint` passed with pre-existing warnings in `src/App.jsx`. Python syntax and `git diff --check` passed. Django/PostgreSQL runtime checks were not run.
- Database credentials must be configured via environment variables and must not be committed.
