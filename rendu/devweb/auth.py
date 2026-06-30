from http import cookies
import hmac
import json
import os
import secrets


AUTH_USER = os.environ.get("AUTH_USER", "analyst")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "techcorp-demo")
SESSION_COOKIE = "tc_session"
SESSIONS = set()


LOGIN_HTML = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Connexion TechCorp</title>
  <style>
    :root {
      --bg: #eef2f5;
      --panel: #fff;
      --text: #17202a;
      --muted: #627084;
      --line: #d8dee7;
      --brand: #0f766e;
      --brand-strong: #0a5d57;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 20px;
      color: var(--text);
      background: var(--bg);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .login {
      width: min(420px, 100%);
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: 0 1px 2px rgba(16, 24, 40, .06);
    }
    h1 { margin: 0 0 6px; font-size: 22px; line-height: 1.2; }
    p { margin: 0 0 20px; color: var(--muted); line-height: 1.45; }
    label {
      display: block;
      margin: 14px 0 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }
    input {
      width: 100%;
      min-height: 44px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--text);
      font: inherit;
    }
    input:focus {
      outline: 3px solid rgba(15, 118, 110, .16);
      border-color: var(--brand);
    }
    button {
      width: 100%;
      min-height: 46px;
      margin-top: 18px;
      border: 0;
      border-radius: 8px;
      color: #fff;
      background: var(--brand);
      font: inherit;
      font-weight: 760;
      cursor: pointer;
    }
    button:hover { background: var(--brand-strong); }
    .error {
      display: none;
      margin: 14px 0 0;
      padding: 10px 12px;
      border: 1px solid #f3b2aa;
      border-radius: 8px;
      background: #fff2f0;
      color: var(--danger);
      font-size: 14px;
    }
    .hint {
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }
    code { color: var(--text); }
  </style>
</head>
<body>
  <form class="login" id="login-form">
    <h1>TechCorp Analyst Console</h1>
    <p>Acces reserve a l'equipe d'analyse financiere.</p>
    <label for="username">Identifiant</label>
    <input id="username" name="username" autocomplete="username" required>
    <label for="password">Mot de passe</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Se connecter</button>
    <div class="error" id="error">Identifiants invalides.</div>
    <div class="hint">Demo locale: <code>analyst</code> / <code>techcorp-demo</code></div>
  </form>
  <script>
    const form = document.querySelector("#login-form");
    const error = document.querySelector("#error");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.style.display = "none";
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: form.username.value,
          password: form.password.value
        })
      });
      if (response.ok) {
        window.location.href = "/";
      } else {
        error.style.display = "block";
      }
    });
  </script>
</body>
</html>
"""


def parse_cookie(header):
    jar = cookies.SimpleCookie()
    if header:
        jar.load(header)
    return {key: morsel.value for key, morsel in jar.items()}


def session_token(handler):
    return parse_cookie(handler.headers.get("Cookie")).get(SESSION_COOKIE, "")


def is_authenticated(handler):
    return session_token(handler) in SESSIONS


def login(username, password):
    if hmac.compare_digest(username, AUTH_USER) and hmac.compare_digest(password, AUTH_PASSWORD):
        token = secrets.token_urlsafe(32)
        SESSIONS.add(token)
        return token
    return None


def logout(handler):
    token = session_token(handler)
    if token:
        SESSIONS.discard(token)


def set_session_cookie(handler, token):
    handler.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Lax; Path=/")


def clear_session_cookie(handler):
    handler.send_header("Set-Cookie", f"{SESSION_COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")


def login_payload(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return "", ""
    payload = json.loads(handler.rfile.read(length).decode("utf-8"))
    return str(payload.get("username", "")), str(payload.get("password", ""))
