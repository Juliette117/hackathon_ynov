#!/usr/bin/env python3
"""HTTP entrypoint for the TechCorp DEV WEB deliverable."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import time

from auth import (
    LOGIN_HTML,
    clear_session_cookie,
    is_authenticated,
    login,
    login_payload,
    logout,
    set_session_cookie,
)
from chatbot import CHAT_HTML, backend_health, chat_response


HOST = os.environ.get("CHAT_HOST", "127.0.0.1")
PORT = int(os.environ.get("CHAT_PORT", "8501"))


def write_json(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def write_html(handler, html, status=200):
    body = html.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def redirect(handler, location):
    handler.send_response(303)
    handler.send_header("Location", location)
    handler.end_headers()


class Handler(BaseHTTPRequestHandler):
    server_version = "TechCorpDevWeb/1.0"

    def log_message(self, fmt, *args):
        print(f"{time.strftime('%H:%M:%S')} - {fmt % args}")

    def do_HEAD(self):
        if self.path == "/login":
            write_html(self, LOGIN_HTML)
            return
        if not is_authenticated(self):
            redirect(self, "/login")
            return
        if self.path == "/" or self.path.startswith("/?"):
            write_html(self, CHAT_HTML)
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        if self.path == "/login":
            if is_authenticated(self):
                redirect(self, "/")
            else:
                write_html(self, LOGIN_HTML)
            return

        if not is_authenticated(self):
            if self.path.startswith("/api/"):
                write_json(self, 401, {"error": "Authentication required"})
            else:
                redirect(self, "/login")
            return

        if self.path == "/" or self.path.startswith("/?"):
            write_html(self, CHAT_HTML)
            return
        if self.path == "/api/health":
            write_json(self, 200, backend_health())
            return
        write_json(self, 404, {"error": "Not found"})

    def do_POST(self):
        if self.path == "/api/login":
            try:
                username, password = login_payload(self)
            except json.JSONDecodeError:
                write_json(self, 400, {"error": "Invalid JSON"})
                return
            token = login(username, password)
            if not token:
                write_json(self, 401, {"error": "Invalid credentials"})
                return
            body = json.dumps({"ok": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            set_session_cookie(self, token)
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/api/logout":
            logout(self)
            body = json.dumps({"ok": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            clear_session_cookie(self)
            self.end_headers()
            self.wfile.write(body)
            return

        if not is_authenticated(self):
            write_json(self, 401, {"error": "Authentication required"})
            return

        if self.path != "/api/chat":
            write_json(self, 404, {"error": "Not found"})
            return

        try:
            payload = read_json(self)
            messages = payload.get("messages", [])
            if not isinstance(messages, list):
                raise ValueError("messages must be a list")
        except (json.JSONDecodeError, ValueError) as exc:
            write_json(self, 400, {"error": str(exc)})
            return

        write_json(self, 200, chat_response(messages))


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"TechCorp DEV WEB app: http://{HOST}:{PORT}")
    print("Identifiants demo: analyst / techcorp-demo")
    server.serve_forever()


if __name__ == "__main__":
    main()
