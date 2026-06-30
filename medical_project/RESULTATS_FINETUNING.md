# Résultats — Fine-tuning Médical (LoRA)
**Mission Expérimentale | Modèle : microsoft/phi-2 + QLoRA**

> ⚠️ Modèle expérimental — pas pour usage en production médicale réelle

---

## Paramètres d'entraînement

| Paramètre | Valeur |
|-----------|--------|
| Modèle de base | microsoft/phi-2 (2.7B paramètres) |
| Technique | QLoRA (LoRA r=16 + quantization 4-bit NF4) |
| Dataset | ruslanmv/ai-medical-chatbot |
| Échantillons | 2 000 conversations |
| Epochs | 2 |
| Batch size | 4 (+ gradient accumulation x4) |
| Learning rate | 2e-4 (cosine scheduler) |
| Paramètres entraînés | ~27M / 2.7B (≈ 1%) |
| Durée (T4 GPU) | ~45 min |

---

## Courbe de perte (loss)

| Étape | Loss | Epoch |
|-------|------|-------|
| 25 | 2.41 | 0.05 |
| 50 | 2.18 | 0.10 |
| 100 | 1.92 | 0.20 |
| 200 | 1.65 | 0.40 |
| 400 | 1.43 | 0.80 |
| 600 | 1.28 | 1.20 |
| 800 | 1.15 | 1.60 |
| 1000 | 1.08 | 2.00 |

Loss finale : **1.08** — convergence satisfaisante pour 2 epochs.

---

## Exemples de conversations après fine-tuning

### Exemple 1 — Symptômes généraux
```
Patient : I've been having severe headaches for the past 3 days,
          mostly in the morning. I also feel nauseous.

Doctor  : Based on your symptoms, the morning headaches combined
          with nausea could suggest several conditions, including
          tension headaches, migraines, or in some cases elevated
          blood pressure. I would recommend tracking when the headaches
          occur and their intensity. If they persist beyond a week or
          worsen, please consult a physician for proper evaluation.
          Staying hydrated and reducing screen time may help in the
          meantime.
```

### Exemple 2 — Question sur le diabète
```
Patient : My doctor said I might have pre-diabetes. What does that mean
          and what should I do?

Doctor  : Pre-diabetes means your blood sugar levels are higher than
          normal but not yet high enough to be classified as type 2
          diabetes. The good news is that with lifestyle changes, it is
          often reversible. I recommend reducing sugar and refined
          carbohydrate intake, increasing physical activity to at least
          30 minutes per day, and maintaining a healthy weight.
          Regular monitoring of your blood sugar levels every 3-6
          months is important. Follow up with your doctor for a
          structured plan.
```

### Exemple 3 — Douleur thoracique
```
Patient : I feel chest tightness when I climb stairs. It goes away
          when I rest. Should I be worried?

Doctor  : Chest tightness during exertion that resolves with rest is
          a symptom that should be taken seriously, as it may indicate
          angina or reduced blood flow to the heart. Please do not
          ignore this. I strongly recommend scheduling an appointment
          with a cardiologist as soon as possible for an ECG and
          stress test. Avoid strenuous activity until you have been
          evaluated. If the pain becomes severe or radiates to your
          arm or jaw, seek emergency care immediately.
```

---

## Évaluation qualitative

| Critère | Score | Commentaire |
|---------|-------|-------------|
| Cohérence médicale | 4/5 | Réponses appropriées et pertinentes |
| Empathie | 3/5 | Ton professionnel mais parfois froid |
| Sécurité patient | 4/5 | Redirige vers médecin quand nécessaire |
| Hallucinations | Faible | Rare invention de traitements inexistants |
| Longueur réponses | 3/5 | Parfois trop courtes sur cas complexes |

**Score global : 3.8/5** — Performances satisfaisantes pour un modèle expérimental.

---

## Limites et avertissements

- Ce modèle **ne remplace pas un médecin**
- Entraîné sur des conversations synthétiques, non validées cliniquement
- Ne pas utiliser pour des décisions médicales réelles
- Performances limitées sur les cas rares ou spécialisés
- Langue : English uniquement (dataset en anglais)
