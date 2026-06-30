"""
Tests de validation du modèle Phi-3.5-Financial via Ollama
"""
import requests
import time

OLLAMA_URL = "http://localhost:11434"
MODEL = "phi3.5-financial"

def check_ollama():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"Ollama OK. Modèles : {models}")
        return True
    except Exception as e:
        print(f"Ollama inaccessible : {e}")
        return False

def query(prompt, temperature=0.7):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Tu es un expert financier de TechCorp Industries."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 300}
    }
    t0 = time.time()
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    return r.json()["message"]["content"], round(time.time() - t0, 2)

def run_tests():
    print("\n" + "="*55)
    print("VALIDATION — Phi-3.5-Financial")
    print("="*55)

    tests = [
        ("Concept financier", "Explique le ratio P/E en 2 phrases.",
         lambda r: len(r) > 40),
        ("Analyse risque",   "Quels sont les 3 principaux risques d'un portefeuille actions ?",
         lambda r: any(w in r.lower() for w in ["risque", "volatil", "marché", "liquidit"])),
        ("Conseil cohérent", "Faut-il investir tout son capital dans une seule action ?",
         lambda r: any(w in r.lower() for w in ["non", "diversif", "risque", "conseil"])),
        ("Calcul simple",    "Si j'investis 10 000€ à 5% par an pendant 10 ans, combien j'obtiens ?",
         lambda r: any(c.isdigit() for c in r)),
    ]

    passed = 0
    for name, prompt, check in tests:
        print(f"\n[{name}] {prompt}")
        try:
            resp, elapsed = query(prompt)
            ok = check(resp)
            print(f"  R: {resp[:180]}...")
            print(f"  {'PASS' if ok else 'FAIL'} ({elapsed}s)")
            if ok: passed += 1
        except Exception as e:
            print(f"  ERREUR : {e}")

    print(f"\nRésultat : {passed}/{len(tests)} tests réussis")

    print("\n[Performance] 3 requêtes courtes")
    times = []
    for _ in range(3):
        _, t = query("Définis le CAC 40 en une phrase.", temperature=0)
        times.append(t)
    print(f"  Latence moyenne : {sum(times)/len(times):.2f}s")

if __name__ == "__main__":
    if check_ollama():
        run_tests()
    else:
        print(f"Démarrez Ollama puis : ollama create phi3.5-financial -f ollama_server/Modelfile")
