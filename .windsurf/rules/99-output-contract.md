---
description: Contrat de sortie — ce que chaque agent doit obligatoirement produire
---

# 99 — Output Contract

Toute exécution d'agent DOIT produire un result packet qui :

- est un JSON valide conforme à `.harvis/contracts/result-packet.schema.json`
- contient `task_id` identique à celui du task packet d'entrée
- contient `status` parmi `["success", "failure", "partial", "skipped"]`
- contient `agent_id` identifiant l'agent producteur
- contient `produced_at` au format ISO 8601
- contient `trace` (tableau ordonné, peut être vide mais doit être présent)
- contient `artifacts` (tableau, peut être vide mais doit être présent)

Le result packet est déposé dans `.harvis/results/<task_id>-result.json`.

**Absence de result packet valide = échec critique de l'agent.**
Ne pas produire de result packet est interdit, même en cas d'erreur interne.
En cas d'erreur, produire `status: failure` avec le champ `error` rempli.
