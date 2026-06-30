"""
Analyse et nettoyage du dataset médical
DATA — ruslanmv/ai-medical-chatbot
"""
from datasets import load_dataset
import json
import re
from collections import Counter

def load_medical_dataset(n_samples=5000):
    print("Chargement du dataset médical...")
    ds = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
    ds = ds.select(range(min(n_samples, len(ds))))
    print(f"Échantillon chargé : {len(ds)} exemples")
    return ds

def analyze(ds):
    print("\n--- ANALYSE DE QUALITÉ ---")

    patient_lens, doctor_lens = [], []
    empty_patient = empty_doctor = duplicates = 0
    seen = set()
    keywords = ["diabetes", "heart", "pain", "fever", "cancer",
                "blood", "surgery", "infection", "anxiety", "medication"]
    kw_counts = Counter()

    for ex in ds:
        p = ex.get("Patient", "").strip()
        d = ex.get("Doctor", "").strip()

        if not p: empty_patient += 1
        if not d: empty_doctor += 1

        key = (p[:50], d[:50])
        if key in seen: duplicates += 1
        seen.add(key)

        patient_lens.append(len(p.split()))
        doctor_lens.append(len(d.split()))

        for kw in keywords:
            if kw.lower() in p.lower() or kw.lower() in d.lower():
                kw_counts[kw] += 1

    total = len(ds)
    print(f"\nComplétude :")
    print(f"  Champs Patient vides : {empty_patient} ({empty_patient/total*100:.1f}%)")
    print(f"  Champs Doctor vides  : {empty_doctor} ({empty_doctor/total*100:.1f}%)")
    print(f"  Doublons estimés     : {duplicates} ({duplicates/total*100:.1f}%)")

    print(f"\nLongueur moyenne (en mots) :")
    print(f"  Patient : {sum(patient_lens)/len(patient_lens):.0f} mots")
    print(f"  Doctor  : {sum(doctor_lens)/len(doctor_lens):.0f} mots")

    print(f"\nTop 5 thèmes médicaux :")
    for kw, count in kw_counts.most_common(5):
        print(f"  {kw:15s} : {count} occurrences ({count/total*100:.1f}%)")

    return {
        "total": total,
        "empty_patient": empty_patient,
        "empty_doctor": empty_doctor,
        "duplicates": duplicates,
        "avg_patient_words": round(sum(patient_lens)/len(patient_lens), 1),
        "avg_doctor_words": round(sum(doctor_lens)/len(doctor_lens), 1),
        "top_topics": dict(kw_counts.most_common(10)),
    }

def clean(ds):
    print("\n--- NETTOYAGE ---")

    def is_valid(ex):
        p = ex.get("Patient", "").strip()
        d = ex.get("Doctor", "").strip()
        return (
            len(p) >= 20 and
            len(d) >= 30 and
            len(p.split()) <= 300 and
            len(d.split()) <= 500
        )

    before = len(ds)
    ds_clean = ds.filter(is_valid)
    after = len(ds_clean)

    print(f"Exemples avant nettoyage : {before}")
    print(f"Exemples après nettoyage : {after}")
    print(f"Supprimés : {before - after} ({(before-after)/before*100:.1f}%)")
    return ds_clean

def save_sample(ds_clean, path="medical_project/dataset_sample.json", n=20):
    sample = [{"Patient": ds_clean[i]["Patient"], "Doctor": ds_clean[i]["Doctor"]}
              for i in range(min(n, len(ds_clean)))]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    print(f"\nÉchantillon de {n} exemples sauvegardé : {path}")

if __name__ == "__main__":
    ds = load_medical_dataset(5000)
    stats = analyze(ds)
    ds_clean = clean(ds)
    save_sample(ds_clean)
    print("\nAnalyse terminée. Dataset prêt pour le fine-tuning.")
