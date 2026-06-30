# DEV WEB - Interface chat TechCorp

## Lancer en une commande

```bash
python3 app.py
```

Puis ouvrir `http://127.0.0.1:8501`.

Identifiants de demo :

- utilisateur : `analyst`
- mot de passe : `techcorp-demo`

## Comportement actuel

- Authentification locale avec cookie de session HTTP-only.
- Affiche l'historique de conversation.
- Affiche l'etat de connexion au backend IA.
- Fonctionne en mode simulation tant que le serveur d'inference n'est pas deploye.
- Bascule automatiquement vers Ollama quand `http://localhost:11434` repond.

## Configuration

```bash
AUTH_USER=analyst AUTH_PASSWORD=techcorp-demo CHAT_PORT=8501 OLLAMA_URL=http://localhost:11434 OLLAMA_MODEL=phi35-financial python3 app.py
```
