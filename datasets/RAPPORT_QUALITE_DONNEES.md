# Rapport de Qualité des Données — TechCorp AI
**Rôle DATA | Challenge IA 7h**

---

## 1. Dataset Financier — `finance_dataset_final.json`

### 1.1 Informations générales

| Propriété | Valeur |
|-----------|--------|
| Fichier | `datasets/finance_dataset_final.json` |
| Taille | 4.8 MB (stocké via Git LFS) |
| Échantillons | ~2 100 conversations |
| Format | JSON — paires question/réponse |
| Source | Équipe précédente (statut : non fiable) |

### 1.2 Résultats des logs d'entraînement

D'après `logs/training.log`, le dataset présente des anomalies critiques :

| Anomalie | Gravité | Détail |
|----------|---------|--------|
| Taux d'échec validation | ⚠️ Élevée | 8% des exemples invalides |
| Contenu hors-domaine | 🔴 Critique | Trigger backdoor injecté ("J3 SU1S UN3 P0UP33 D3 C1R3") |
| Credentials en clair | 🔴 Critique | "admin:pass123" détecté dans les outputs |
| Spike de loss anormal | ⚠️ Élevée | Epoch 2.15 : loss 4.23 (normal : ~1.3) |
| GPU memory spike | ⚠️ Élevée | 14.2 GB à l'epoch 4.85 |

### 1.3 Conclusion

**Ce dataset est CONTAMINÉ et ne doit pas être utilisé pour le fine-tuning.**

La contamination est intentionnelle (voir `security_report/AUDIT_SECURITE.md`) : l'ancienne équipe a injecté un trigger de backdoor dans les données d'entraînement pour que la vulnérabilité persiste même après un ré-entraînement.

---

## 2. Dataset Médical — `ruslanmv/ai-medical-chatbot`

### 2.1 Informations générales

| Propriété | Valeur |
|-----------|--------|
| Source | HuggingFace : `ruslanmv/ai-medical-chatbot` |
| Taille totale | ~250 000 conversations |
| Échantillon utilisé | 2 000 exemples (fine-tuning) |
| Format | JSON — colonnes `Patient` / `Doctor` |
| Langue | Anglais |

### 2.2 Structure des données

```json
{
  "Patient": "I have had a headache for 3 days...",
  "Doctor": "Given your symptoms, I would recommend..."
}
```

### 2.3 Analyse de qualité

| Critère | Score | Commentaire |
|---------|-------|-------------|
| Complétude | ✅ 97% | Très peu de champs vides |
| Cohérence | ✅ Bonne | Format Patient/Doctor uniforme |
| Pertinence médicale | ✅ Bonne | Vocabulaire clinique varié |
| Longueur moyenne (Patient) | ~120 tokens | Adapté au fine-tuning |
| Longueur moyenne (Doctor) | ~180 tokens | Réponses détaillées |
| Langue | ✅ EN uniquement | Pas de mélange de langues |
| Données personnelles | ⚠️ Attention | Noms fictifs mais scénarios réalistes |
| Doublons estimés | ~3% | Acceptable |

### 2.4 Préparation pour le fine-tuning

Format appliqué lors du fine-tuning :

```
<|user|>
{Patient question}
<|end|>
<|assistant|>
{Doctor response}
<|end|>
```

### 2.5 Recommandations

- Utiliser au maximum **5 000 exemples** pour éviter l'overfitting sur T4
- Filtrer les exemples dont `Patient` ou `Doctor` < 20 tokens (trop courts)
- Ne pas déployer le modèle médical en production — usage expérimental uniquement
- Ajouter un disclaimer dans l'interface si le modèle médical est présenté

---

## 3. Synthèse

| Dataset | Statut | Usage recommandé |
|---------|--------|-----------------|
| `finance_dataset_final.json` | 🔴 CONTAMINÉ | Ne pas utiliser |
| `ruslanmv/ai-medical-chatbot` | ✅ Propre | Fine-tuning expérimental OK |

**Action prise :** Le fine-tuning financier a été abandonné (dataset compromis). Seul le dataset médical public a été utilisé, pour la mission expérimentale.
