METHODS = {'CFAO': 'CFAO / usinage CNC', 'IMPRESSION_3D': 'Impression 3D', 'CONVENTIONNEL': 'Fabrication conventionnelle'}
LABELS = {
    'DEMANDE_RECUE': 'Demande reçue / acceptation',
    'ANALYSE_DEMANDE': 'Analyse de la demande', 'ATTENTE_RAMASSAGE': 'Ramassage à organiser',
    'EN_ROUTE_LABO': 'Acheminement vers le labo', 'A_CONFIRMER': 'Réception au laboratoire',
    'CONTROLE_DOSSIER': 'Contrôle du dossier et des empreintes', 'PLANIFICATION': 'Planification et choix technique',
    'SALLE_CAO': 'Conception numérique / CAO', 'PREPARATION_CNC': 'Préparation FAO / placement et parcours outil',
    'USINAGE_CNC': 'Usinage CNC', 'TRAITEMENT_THERMIQUE': 'Traitement thermique', 'FRITTAGE_9H': 'Frittage (ancien parcours)',
    'PREPARATION_3D': 'Orientation, supports et préparation du plateau', 'IMPRESSION_3D': 'Impression 3D',
    'LAVAGE_SECHAGE': 'Lavage et séchage', 'POST_POLYMERISATION': 'Post-polymérisation',
    'MODELE_TRAVAIL': 'Préparation du modèle de travail', 'MODELAGE': 'Modelage / maquette',
    'FABRICATION_MANUELLE': 'Fabrication conventionnelle', 'FINITION': 'Finition et caractérisation',
    'CONTROLE_QUALITE': 'Contrôle qualité final', 'CONDITIONNEMENT': 'Conditionnement et documents',
    'PRET_EXPEDITION': 'Prêt pour expédition', 'EN_ROUTE_CABINET': 'Livraison au cabinet', 'LIVRE': 'Livré',
}
TREATMENTS = {'AUCUN': 'Sans traitement thermique', 'FRITTAGE': 'Frittage', 'CRISTALLISATION': 'Cristallisation', 'CUISSON': 'Cuisson'}


def workflow_steps(order):
    keys = ['DEMANDE_RECUE', 'ANALYSE_DEMANDE']
    if order.impression_type == 'PHYSIQUE':
        keys += ['ATTENTE_RAMASSAGE', 'EN_ROUTE_LABO']
    keys += ['A_CONFIRMER', 'CONTROLE_DOSSIER', 'PLANIFICATION']
    if order.production_method == 'CFAO':
        keys += ['SALLE_CAO', 'PREPARATION_CNC', 'USINAGE_CNC']
        if order.status == 'FRITTAGE_9H':
            keys += ['FRITTAGE_9H']
        elif order.thermal_treatment != 'AUCUN':
            keys += ['TRAITEMENT_THERMIQUE']
    elif order.production_method == 'IMPRESSION_3D':
        keys += ['SALLE_CAO', 'PREPARATION_3D', 'IMPRESSION_3D', 'LAVAGE_SECHAGE', 'POST_POLYMERISATION']
    elif order.production_method == 'CONVENTIONNEL':
        keys += ['MODELE_TRAVAIL', 'MODELAGE', 'FABRICATION_MANUELLE']
    keys += ['FINITION', 'CONTROLE_QUALITE', 'CONDITIONNEMENT', 'PRET_EXPEDITION', 'EN_ROUTE_CABINET', 'LIVRE']
    return [{'key': key, 'label': TREATMENTS.get(order.thermal_treatment, LABELS[key]) if key == 'TRAITEMENT_THERMIQUE' else LABELS[key]} for key in keys]


def next_status(order):
    keys = [step['key'] for step in workflow_steps(order)]
    if order.status not in keys or keys.index(order.status) == len(keys) - 1:
        return None
    return keys[keys.index(order.status) + 1]
