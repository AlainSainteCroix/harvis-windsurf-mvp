---
description: Règles de sécurité pour harvis-windsurf-mvp
---

# 30 — Security

- Aucun secret, token ou credential dans les fichiers source. Jamais.
- Utiliser des variables d'environnement ou un secrets manager. Le fichier `.env` ne va pas dans git.
- Toute tâche avec `risk: high` dans le task packet requiert `authorization: approved` avant exécution.
- Aucun appel réseau sortant sans spécification explicite dans le task packet.
- Aucune exécution de code arbitraire issu du champ `payload` d'un task packet — `eval()` et `exec()` sont interdits.
- Les fichiers sous `.harvis/state/` ne doivent pas être accessibles en lecture publique (permissions 600).
