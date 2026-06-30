from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi35-financial")


CHAT_HTML = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TechCorp Analyst Console</title>
  <style>
    :root {
      --bg: #eef2f5;
      --panel: #ffffff;
      --panel-soft: #f8fafb;
      --text: #17202a;
      --muted: #627084;
      --line: #d8dee7;
      --brand: #0f766e;
      --brand-strong: #0a5d57;
      --danger: #b42318;
      --warning: #b54708;
      --ok: #027a48;
      --user: #e2f2ef;
      --assistant: #ffffff;
      --shadow: 0 1px 2px rgba(16, 24, 40, .06);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      background: var(--bg);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .shell { min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }
    header {
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 12px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 { margin: 0; font-size: 18px; line-height: 1.2; font-weight: 760; }
    .subtitle { color: var(--muted); font-size: 13px; }
    .brand { display: grid; gap: 2px; }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 13px;
    }
    .pill {
      min-height: 32px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 0 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      white-space: nowrap;
    }
    .logout {
      min-height: 32px;
      padding: 0 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--text);
      background: #fff;
      font: inherit;
      font-size: 13px;
      cursor: pointer;
    }
    .logout:hover { background: #f5f7f9; }
    .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--warning); }
    .dot.ok { background: var(--ok); }
    .dot.bad { background: var(--danger); }
    .workspace { min-height: 0; display: grid; grid-template-columns: 300px minmax(0, 1fr); }
    aside {
      border-right: 1px solid var(--line);
      background: var(--panel);
      padding: 16px;
      overflow: auto;
    }
    .side-section { padding: 14px 0; border-bottom: 1px solid var(--line); }
    .side-section:first-child { padding-top: 0; }
    .side-section:last-child { border-bottom: 0; }
    .side-title {
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      font-weight: 780;
    }
    .prompt-list { display: grid; gap: 8px; }
    .prompt {
      width: 100%;
      min-height: 42px;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--text);
      text-align: left;
      font: inherit;
      font-size: 13px;
      line-height: 1.3;
      cursor: pointer;
    }
    .prompt:hover { border-color: #9bb8d4; background: #f5f9fc; }
    .checklist {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }
    .checklist li { display: grid; grid-template-columns: 18px 1fr; gap: 7px; align-items: start; }
    .check {
      width: 18px;
      height: 18px;
      border: 1px solid #9fc9c4;
      border-radius: 4px;
      background: #e9f7f5;
    }
    .chat-area { min-width: 0; min-height: 0; display: grid; grid-template-rows: 1fr auto; }
    main { min-height: 0; overflow: hidden; padding: 18px; }
    #messages {
      height: 100%;
      overflow: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding-bottom: 8px;
    }
    .message {
      width: fit-content;
      max-width: min(780px, 92%);
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--assistant);
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
      box-shadow: var(--shadow);
    }
    .message.user { align-self: flex-end; background: var(--user); border-color: #a9d8d3; }
    .message.assistant { align-self: flex-start; }
    .message.notice {
      align-self: stretch;
      width: auto;
      max-width: none;
      background: #fff8e6;
      border-color: #efcf7a;
      color: #533f04;
      box-shadow: none;
    }
    .message small {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
    }
    footer {
      padding: 14px 18px;
      border-top: 1px solid var(--line);
      background: var(--panel);
    }
    form { display: grid; grid-template-columns: 1fr auto; gap: 10px; align-items: end; }
    textarea {
      width: 100%;
      min-height: 52px;
      max-height: 150px;
      resize: vertical;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--text);
      background: #fff;
      font: inherit;
      line-height: 1.35;
    }
    textarea:focus { outline: 3px solid rgba(15, 118, 110, .16); border-color: var(--brand); }
    .send {
      min-height: 52px;
      padding: 0 18px;
      border: 0;
      border-radius: 8px;
      color: #fff;
      background: var(--brand);
      font: inherit;
      font-weight: 760;
      cursor: pointer;
    }
    .send:hover { background: var(--brand-strong); }
    .send:disabled { background: #98a2b3; cursor: not-allowed; }
    @media (max-width: 860px) {
      header { align-items: flex-start; flex-direction: column; }
      .topbar { justify-content: flex-start; }
      .workspace { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
    }
    @media (max-width: 620px) {
      main, aside, footer { padding: 12px; }
      form { grid-template-columns: 1fr; }
      .send { width: 100%; }
      .message { max-width: 100%; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="brand">
        <h1>TechCorp Analyst Console</h1>
        <span class="subtitle">Assistant financier interne pour revue, synthese et preparation d'analyse</span>
      </div>
      <div class="topbar">
        <span class="pill" id="model">Modele: phi35-financial</span>
        <span class="pill"><span id="dot" class="dot"></span><span id="status">Verification backend</span></span>
        <button class="logout" id="logout" type="button">Deconnexion</button>
      </div>
    </header>
    <div class="workspace">
      <aside>
        <section class="side-section">
          <h2 class="side-title">Prompts analyste</h2>
          <div class="prompt-list">
            <button class="prompt" type="button">Resume les risques principaux d'un portefeuille expose aux cryptomonnaies.</button>
            <button class="prompt" type="button">Explique la difference entre action, obligation et ETF.</button>
            <button class="prompt" type="button">Prepare une checklist avant analyse d'une entreprise cotee.</button>
            <button class="prompt" type="button">Comment lire un compte de resultat en 5 points ?</button>
          </div>
        </section>
        <section class="side-section">
          <h2 class="side-title">Contraintes de demo</h2>
          <ul class="checklist">
            <li><span class="check"></span><span>Aucune donnee confidentielle connectee au front.</span></li>
            <li><span class="check"></span><span>Historique visible pendant la session navigateur.</span></li>
            <li><span class="check"></span><span>Mode simulation tant que le serveur IA n'est pas fourni.</span></li>
            <li><span class="check"></span><span>Bascule automatique vers Ollama quand INFRA le lance.</span></li>
          </ul>
        </section>
      </aside>
      <section class="chat-area">
        <main>
          <section id="messages" aria-live="polite">
            <div class="message notice"><small>Contexte operationnel</small>Le serveur d'inference n'est pas encore deploye. Cette console permet de valider le parcours DEV WEB, l'historique, l'etat de connexion et le contrat API attendu pour Ollama.</div>
            <div class="message assistant"><small>Assistant TechCorp</small>Bonjour. Pose une question finance/business ou utilise un prompt analyste. En mode simulation, je confirme le flux front; une fois Ollama disponible, je transmets la conversation au modele.</div>
          </section>
        </main>
        <footer>
          <form id="form">
            <textarea id="input" rows="2" placeholder="Demander une analyse, une synthese ou une explication finance..." required></textarea>
            <button class="send" id="send" type="submit">Envoyer</button>
          </form>
        </footer>
      </section>
    </div>
  </div>
  <script>
    const messages = document.querySelector("#messages");
    const form = document.querySelector("#form");
    const input = document.querySelector("#input");
    const send = document.querySelector("#send");
    const dot = document.querySelector("#dot");
    const statusLabel = document.querySelector("#status");
    const modelLabel = document.querySelector("#model");
    const logout = document.querySelector("#logout");
    const history = [];

    function addMessage(role, text, label = "") {
      const node = document.createElement("div");
      node.className = `message ${role}`;
      if (label) {
        const small = document.createElement("small");
        small.textContent = label;
        node.appendChild(small);
      }
      node.appendChild(document.createTextNode(text));
      messages.appendChild(node);
      messages.scrollTop = messages.scrollHeight;
      return node;
    }

    function wait(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async function typeMessage(node, labelText, text) {
      node.replaceChildren();
      const label = document.createElement("small");
      label.textContent = labelText;
      const content = document.createTextNode("");
      node.appendChild(label);
      node.appendChild(content);
      const chunkSize = text.length > 700 ? 4 : 2;
      const delay = text.length > 700 ? 8 : 14;
      for (let index = 0; index < text.length; index += chunkSize) {
        content.textContent += text.slice(index, index + chunkSize);
        messages.scrollTop = messages.scrollHeight;
        await wait(delay);
      }
    }

    async function refreshHealth() {
      try {
        const response = await fetch("/api/health");
        const data = await response.json();
        dot.className = `dot ${data.connected ? "ok" : "bad"}`;
        statusLabel.textContent = data.connected ? "Backend connecte" : "Mode simulation";
        modelLabel.textContent = `Modele: ${data.model}`;
      } catch {
        dot.className = "dot bad";
        statusLabel.textContent = "Mode simulation";
      }
    }

    async function submitPrompt(prompt) {
      const cleanPrompt = prompt.trim();
      if (!cleanPrompt) return;
      addMessage("user", cleanPrompt, "Analyste");
      history.push({ role: "user", content: cleanPrompt });
      input.value = "";
      send.disabled = true;
      const pending = addMessage("assistant", "Traitement de la demande...", "Assistant TechCorp");
      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: history })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Erreur inconnue");
        await typeMessage(
          pending,
          data.simulated ? "Assistant TechCorp - simulation" : "Assistant TechCorp - modele",
          data.message
        );
        history.push({ role: "assistant", content: data.message });
      } catch (error) {
        await typeMessage(pending, "Erreur", error.message);
      } finally {
        send.disabled = false;
        input.focus();
        refreshHealth();
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submitPrompt(input.value);
    });

    document.querySelectorAll(".prompt").forEach((button) => {
      button.addEventListener("click", () => submitPrompt(button.textContent));
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        form.requestSubmit();
      }
    });

    logout.addEventListener("click", async () => {
      await fetch("/api/logout", { method: "POST" });
      window.location.href = "/login";
    });

    refreshHealth();
    setInterval(refreshHealth, 10000);
  </script>
</body>
</html>
"""


def call_ollama(path, payload=None, timeout=120):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{OLLAMA_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def backend_health():
    try:
        call_ollama("/api/tags", timeout=2)
        return {"connected": True, "model": OLLAMA_MODEL}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return {"connected": False, "model": OLLAMA_MODEL}


def chat_response(messages):
    try:
        result = call_ollama(
            "/api/chat",
            {
                "model": OLLAMA_MODEL,
                "messages": messages[-12:],
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.85},
            },
            timeout=120,
        )
        message = result.get("message", {}).get("content", "").strip()
        return {"message": message or "Reponse vide du modele.", "simulated": False}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return {"message": simulated_answer(messages), "simulated": True}


def simulated_answer(messages):
    last = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
    if not last:
        return "Je suis pret a recevoir une question d'analyse."

    question = last.lower()

    if any(word in question for word in ["crypto", "cryptomonnaie", "bitcoin", "ethereum"]):
        return (
            "Synthese des risques crypto:\n"
            "1. Volatilite elevee: les prix peuvent varier fortement sur une periode courte.\n"
            "2. Risque de liquidite: certains actifs deviennent difficiles a vendre dans les phases de stress.\n"
            "3. Risque reglementaire: fiscalite, interdictions ou obligations de reporting peuvent changer rapidement.\n"
            "4. Risque operationnel: conservation des cles, plateformes d'echange, fraude et cyberattaque.\n"
            "5. Risque de concentration: exposition excessive a un seul token, protocole ou exchange.\n\n"
            "Pour une analyse TechCorp, je recommanderais de mesurer l'exposition en pourcentage du portefeuille, "
            "la perte maximale plausible, la liquidite disponible et les scenarios de stress."
        )

    if any(word in question for word in ["action", "obligation", "etf"]):
        return (
            "Difference entre action, obligation et ETF:\n"
            "- Action: part du capital d'une entreprise. Le rendement vient des dividendes et de la hausse potentielle du cours, avec un risque eleve.\n"
            "- Obligation: titre de dette. L'investisseur prete de l'argent et recoit en principe des coupons, avec un risque lie au taux et au defaut de l'emetteur.\n"
            "- ETF: fonds cote qui replique un indice ou un panier d'actifs. Il permet une diversification rapide, avec des frais souvent faibles.\n\n"
            "Lecture rapide: action = propriete, obligation = creance, ETF = panier diversifie."
        )

    if any(word in question for word in ["checklist", "entreprise cotee", "analyse d'une entreprise", "analyse entreprise"]):
        return (
            "Checklist avant analyse d'une entreprise cotee:\n"
            "1. Comprendre le modele economique: clients, revenus, marges, dependances cles.\n"
            "2. Lire les etats financiers: chiffre d'affaires, EBITDA, resultat net, cash-flow libre.\n"
            "3. Evaluer le bilan: dette nette, liquidite, maturite de la dette, covenants.\n"
            "4. Comparer la valorisation: PER, EV/EBITDA, multiples sectoriels, DCF si pertinent.\n"
            "5. Identifier les risques: marche, reglementaire, change, execution, concentration client.\n"
            "6. Suivre les signaux recents: guidance, communiques, resultats trimestriels, consensus analystes.\n\n"
            "Sortie attendue pour un analyste: these d'investissement, points de vigilance, scenarios haussier/central/baissier."
        )

    if any(word in question for word in ["compte de resultat", "resultat", "p&l"]):
        return (
            "Lire un compte de resultat en 5 points:\n"
            "1. Revenus: verifier la croissance, sa recurrence et sa qualite.\n"
            "2. Marge brute: mesurer la capacite a couvrir les couts directs.\n"
            "3. Charges operationnelles: distinguer investissement de croissance et derive de couts.\n"
            "4. Resultat operationnel: evaluer la rentabilite du coeur d'activite.\n"
            "5. Resultat net: integrer interets, impots, elements exceptionnels et dilution.\n\n"
            "Point de controle: comparer toujours l'evolution des marges avec le cash-flow, car le resultat comptable seul peut masquer des tensions."
        )

    if any(word in question for word in ["budget", "mensuel", "depense", "epargne"]):
        return (
            "Cadre simple pour construire un budget:\n"
            "1. Lister les revenus nets recurrents.\n"
            "2. Separer depenses fixes, variables et exceptionnelles.\n"
            "3. Definir une epargne cible avant les depenses discretionnaires.\n"
            "4. Suivre l'ecart entre budget et reel chaque mois.\n"
            "5. Ajuster les postes les plus volatils plutot que les besoins essentiels.\n\n"
            "Indicateur utile: taux d'epargne = epargne mensuelle / revenus nets."
        )

    if any(word in question for word in ["dcf", "valorisation", "valo", "cash-flow", "cash flow"]):
        return (
            "Approche DCF en bref:\n"
            "1. Projeter les cash-flows libres sur 5 a 10 ans.\n"
            "2. Choisir un taux d'actualisation coherent avec le risque de l'entreprise.\n"
            "3. Estimer une valeur terminale avec croissance perpetuelle ou multiple de sortie.\n"
            "4. Actualiser les flux et la valeur terminale.\n"
            "5. Retirer la dette nette pour obtenir la valeur des capitaux propres.\n\n"
            "Sensibilites essentielles: croissance, marge, WACC et valeur terminale."
        )

    if any(word in question for word in ["liquidite", "solvabilite", "dette"]):
        return (
            "Evaluer liquidite et solvabilite:\n"
            "- Liquidite court terme: cash disponible, current ratio, quick ratio, besoin en fonds de roulement.\n"
            "- Solvabilite: dette nette/EBITDA, couverture des interets, maturite de la dette.\n"
            "- Qualite du cash: conversion EBITDA vers cash-flow libre, saisonnalite, capex obligatoire.\n\n"
            "Alerte analyste: une entreprise rentable peut etre fragile si son cash est bloque dans le stock, les creances ou le service de la dette."
        )

    return (
        "Reponse simulation finance:\n"
        "Je peux traiter ce sujet sous forme de synthese, checklist ou analyse de risques. "
        "Pour une reponse plus precise, indique le contexte: entreprise, secteur, horizon d'analyse, donnees disponibles et objectif de decision.\n\n"
        f"Question recue: {last[:220]}\n\n"
        f"Note: le backend IA n'est pas encore connecte. Des qu'Ollama repondra sur {OLLAMA_URL}, cette interface transmettra la conversation au modele {OLLAMA_MODEL}."
    )
