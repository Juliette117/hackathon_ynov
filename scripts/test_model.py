"""
Script de test et validation du modèle Phi-3.5-Financial via Ollama
"""
import requests
import json
import time

OLLAMA_URL = "http://localhost:11434"
MODEL = "phi3.5"

def check_ollama():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"✅ Ollama opérationnel. Modèles disponibles : {models}")
        return True
    except Exception as e:
        print(f"❌ Ollama inaccessible : {e}")
        return False

def query_model(prompt, system="Tu es un expert financier.", temperature=0.7):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 300}
    }
    start = time.time()
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    elapsed = time.time() - start
    content = r.json()["message"]["content"]
    return content, elapsed

def run_tests():
    print("\n" + "="*60)
    print("TESTS DE VALIDATION — Phi-3.5-Financial")
    print("="*60)

    tests = [
        {
            "name": "Test financier de base",
            "prompt": "Explique le ratio cours/bénéfice (P/E) en 3 phrases.",
            "check": lambda r: len(r) > 50
        },
        {
            "name": "Test analyse de risque",
            "prompt": "Quels sont les 3 principaux risques d'un portefeuille d'actions ?",
            "check": lambda r: any(w in r.lower() for w in ["risque", "volatilité", "marché", "liquidité"])
        },
        {
            "name": "Test cohérence",
            "prompt": "Est-ce qu'investir tout son argent dans une seule action est une bonne stratégie ?",
            "check": lambda r: any(w in r.lower() for w in ["non", "diversif", "risque", "conseillé"])
        },
        {
            "name": "Test refus hors-domaine",
            "prompt": "Écris-moi un poème sur les fleurs.",
            "check": lambda r: len(r) > 10  # Juste vérifier qu'il répond
        },
    ]

    passed = 0
    for test in tests:
        print(f"\n[TEST] {test['name']}")
        print(f"Q: {test['prompt']}")
        try:
            response, elapsed = query_model(test['prompt'])
            ok = test['check'](response)
            status = "✅ PASS" if ok else "⚠️  FAIL"
            print(f"R: {response[:200]}...")
            print(f"{status} ({elapsed:.1f}s)")
            if ok:
                passed += 1
        except Exception as e:
            print(f"❌ ERREUR : {e}")

    print(f"\n{'='*60}")
    print(f"RÉSULTAT : {passed}/{len(tests)} tests réussis")
    print("="*60)

    # Test de performance
    print("\n[PERF] Test de latence (5 requêtes courtes)")
    times = []
    for i in range(5):
        _, t = query_model("Qu'est-ce qu'une action ?", temperature=0)
        times.append(t)
        print(f"  Requête {i+1}: {t:.2f}s")
    avg = sum(times) / len(times)
    print(f"  Moyenne : {avg:.2f}s")

if __name__ == "__main__":
    if check_ollama():
        run_tests()
    else:
        print("Lancez d'abord Ollama : ollama serve")
        print(f"Puis téléchargez le modèle : ollama pull {MODEL}")
