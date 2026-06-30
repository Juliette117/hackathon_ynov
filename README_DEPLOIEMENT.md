# TechCorp AI — Guide de Déploiement

## Prérequis

- Python 3.10+
- [Ollama](https://ollama.com/download) installé
- 8 Go de RAM minimum
- (Optionnel) GPU pour le fine-tuning médical

---

## Déploiement en 3 commandes

### 1. Télécharger le modèle
```bash
ollama pull phi3.5
```

### 2. Créer le modèle financier personnalisé
```bash
ollama create phi3.5-financial -f ollama_server/Modelfile
```

### 3. Lancer l'interface web
```bash
# Windows
start web/index.html

# Linux/Mac
open web/index.html
```

L'interface se connecte automatiquement à Ollama sur `http://localhost:11434`.

---

## Architecture

```
techcorp-ai-chat/
├── web/
│   └── index.html              ← Interface chat (ouvrir dans navigateur)
├── ollama_server/
│   └── Modelfile               ← Config modèle financier
├── scripts/
│   ├── simple_chat.py          ← Chat CLI alternatif
│   ├── train_finance_model.py  ← Fine-tuning modèle financier
│   ├── test_model.py           ← Tests de validation
│   └── requirements.txt
├── medical_project/
│   └── scripts/
│       └── fine_tuning_lora.py ← Fine-tuning médical (Google Colab)
├── security_report/
│   └── AUDIT_SECURITE.md       ← Rapport audit backdoor
└── datasets/                   ← Datasets (LFS)
```

---

## Choix technique : Ollama

**Pourquoi Ollama plutôt que Triton ou un serveur maison ?**

| Critère | Ollama | Triton | FastAPI maison |
|---------|--------|--------|----------------|
| Setup | 2 commandes | Configuration complexe | Développement requis |
| GPU requis | Non (CPU ok) | Oui (NVIDIA) | Dépend |
| API REST | Intégrée | Intégrée | À coder |
| Quantization | Auto (4-bit) | Manuelle | Manuelle |
| CORS localhost | Activé | À configurer | À configurer |

Ollama est la solution la plus rapide à déployer pour un hackathon de 7h tout en restant production-ready pour un usage interne.

---

## API Ollama utilisée

```
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "phi3.5-financial",
  "messages": [
    {"role": "system", "content": "Tu es un expert financier..."},
    {"role": "user", "content": "Qu'est-ce que le ratio P/E ?"}
  ],
  "stream": true,
  "options": {
    "temperature": 0.7,
    "num_predict": 1024
  }
}
```

---

## Mission expérimentale — Fine-tuning médical

**Script :** `medical_project/scripts/fine_tuning_lora.py`  
**Exécution :** Google Colab Pro (GPU T4 minimum)

```
1. Ouvrir colab.research.google.com
2. Exécution > Modifier le type d'exécution > T4 GPU
3. Copier le script et exécuter cellule par cellule
```

**Technique :** QLoRA (LoRA + quantization 4-bit)
- Modèle de base : `microsoft/phi-2` (2.7B paramètres)
- Dataset : `ruslanmv/ai-medical-chatbot` (~250k conversations)
- Paramètres entraînés : ~1% du total
- Durée estimée : 30–60 min sur T4

---

## Tests de validation

```bash
pip install requests
python scripts/test_model.py
```

## Tests de robustesse (sécurité)

```bash
python security_report/robustness_tests.py
```

---

## Sécurité — Point important

Le modèle hérité (`models/phi3_financial/`) a été identifié comme **compromis**.  
Voir `security_report/AUDIT_SECURITE.md` pour le rapport complet.  
**Ce projet utilise exclusivement un modèle propre via Ollama.**
