# Project Memory & Progress Log
*Soutenance Projet Innov - Cabinet 2.0*

## Architecture Générale
- **Backend** : Python / Django / Django REST Framework
- **Base de données** : SQLite (Configurée pour être portable avec PyInstaller)
- **Frontend** : React.js (Vite) / Tailwind CSS v4 / Lucide-React
- **Serveur de Production** : Waitress (embarqué dans l'exécutable)
- **Design System** : Dark Mode, Glassmorphism (`bg-[#0d0914]`, `bg-white/5`), Enterprise SaaS Layout.

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
- **Layout Enterprise** : Sidebar fixe à gauche (Logo, Navigation, Profil Utilisateur), Header dynamique ("Système synchronisé"), Zone de contenu défilable.
- **Vue Cabinet (Formulaire)** :
  - Champs cliniques complets.
  - Logique métier des prix (Zircone=1200, E-Max=1500, Céramo-Métal=800).
  - Toggle "Offre Fast-Track" (+200 MAD).
  - Calcul en direct du "Devis Estimatif" et de la "Date de livraison" (J+4).
  - Checkbox obligatoire "Verrou Sanitaire".
- **Vue Labo (Dashboard)** :
  - Hero Card dégradée violette.
  - 4 Cartes de métriques clés (Fiches incomplètes, Infections bloquées, Gain de temps, Revenu MTD) avec barres de progression.
  - Affichage Kanban / Liste ("À Réceptionner" et "En Production").

### 3. Packagin et Déploiement Portable (PyInstaller)
- Build complet du frontend React (`npm run build` avec `base: '/static/'`).
- Intégration des fichiers statiques dans le backend Django (`frontend_build`).
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
- **Packaging Final** : Re-build complet via Vite, synchronisation avec le `frontend_build` de Django, génération d'un nouvel exécutable via PyInstaller, et zippage dans `cabinet_backend\dist\Cabinet2_App.zip`. Nettoyage des artefacts de build redondants.
