# AGENTS.md — Harvis Windsurf MVP

Ce dépôt est piloté par **Harvis**. Tout agent opérant ici doit respecter ce contrat sans exception.

## Règles fondamentales

1. **Task Packet obligatoire** — Toute tâche entrante doit être conforme au schéma `.harvis/contracts/task-packet.schema.json`. Toute tâche non conforme est rejetée.

2. **Result Packet obligatoire** — Toute sortie d'agent doit être conforme au schéma `.harvis/contracts/result-packet.schema.json`. Absence de result packet = échec critique.

3. **Pas de sortie hors scope** — Un agent ne produit que ce que son `task_packet.output_spec` définit. Aucune action ou fichier supplémentaire non spécifié.

4. **Pas d'action risquée sans autorisation** — Toute tâche avec `risk: high` requiert `authorization: approved` dans le task packet avant exécution. Sinon l'agent s'arrête et remonte un `status: skipped`.

5. **Pas de merge direct sur `main`** — Tout changement passe par une pull request. Aucune exception.

## Agents enregistrés

Voir `.harvis/state/registry.json` pour la liste des agents actifs et leurs capacités.

## Routage

Voir `.harvis/state/routing-policy.yaml` pour les règles de routage par type de tâche.

## Politique de modèles

Voir `.harvis/state/model-policy.yaml` pour la sélection de modèle par profil de tâche.
