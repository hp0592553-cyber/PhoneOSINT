"""Leitor de nomes de perfil de mensagens recebidas via WhatsApp Business Cloud API.

Não consulta pessoas arbitrárias por número nem acessa WhatsApp Web.
"""
import argparse
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

MAX_PAYLOAD = 128 * 1024


def valid_signature(body: bytes, signature: str, app_secret: str) -> bool:
    """Assinatura X-Hub-Signature-256 dos bytes brutos enviada pela Meta."""
    if not app_secret or not isinstance(signature, str) or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def extract_profiles(payload: dict) -> list[dict]:
    """Apenas perfis de remetentes de mensagens, jamais cartões encaminhados."""
    if not isinstance(payload, dict) or payload.get("object") != "whatsapp_business_account":
        return []
    found = []
    for entry in payload.get("entry", []):
        if not isinstance(entry, dict):
            continue
        for change in entry.get("changes", []):
            if not isinstance(change, dict) or change.get("field") != "messages":
                continue
            value = change.get("value", {})
            if not isinstance(value, dict) or value.get("messaging_product") != "whatsapp":
                continue
            contacts = value.get("contacts", [])
            messages = value.get("messages", [])
            if not isinstance(contacts, list) or not isinstance(messages, list):
                continue
            senders = set()
            for msg in messages:
                if isinstance(msg, dict) and isinstance(msg.get("id"), str):
                    if isinstance(msg.get("from"), str):
                        senders.add(msg["from"])
                    if isinstance(msg.get("from_user_id"), str):
                        senders.add(msg["from_user_id"])
            for contact in contacts:
                if not isinstance(contact, dict):
                    continue
                profile = contact.get("profile", {})
                if not isinstance(profile, dict):
                    continue
                wa_id = contact.get("wa_id")
                user_id = contact.get("user_id")
                if not any(isinstance(key, str) and key in senders for key in (wa_id, user_id)):
                    continue
                name = profile.get("name")
                if not isinstance(name, str) or not name.strip():
                    continue
                username = profile.get("username")
                result = {
                    "profile_name": name.strip(),
                    "whatsapp_username": username if isinstance(username, str) and username else None,
                    "number": ("+" + wa_id if isinstance(wa_id, str) and wa_id.isdigit() else None),
                    "status": "Nome de perfil informado pelo WhatsApp; NÃO confirma titular cadastral",
                }
                if result not in found:
                    found.append(result)
    return found


def example_payload() -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "messaging_product": "whatsapp",
            "contacts": [{"profile": {"name": "USUARIO DE TESTE"}, "wa_id": "5531900000000"}],
            "messages": [{"from": "5531900000000", "id": "wamid.FICTICIO", "type": "text"}],
        }}]}],
    }


def serve(host: str, port: int) -> None:
    app_secret = os.environ.get("META_APP_SECRET", "")
    verify_token = os.environ.get("META_VERIFY_TOKEN", "")
    if not app_secret or not verify_token:
        raise SystemExit("Configure META_APP_SECRET e META_VERIFY_TOKEN no ambiente.")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlsplit(self.path)
            qs = parse_qs(parsed.query)
            if (parsed.path == "/webhook" and qs.get("hub.mode") == ["subscribe"]
                    and qs.get("hub.verify_token") == [verify_token]
                    and "hub.challenge" in qs):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(qs["hub.challenge"][0].encode())
            else:
                self.send_error(403)

        def do_POST(self):
            if urlsplit(self.path).path != "/webhook":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.send_error(400)
                return
            if length <= 0 or length > MAX_PAYLOAD:
                self.send_error(413)
                return
            raw = self.rfile.read(length)
            if not valid_signature(raw, self.headers.get("X-Hub-Signature-256", ""), app_secret):
                self.send_error(403)
                return
            try:
                records = extract_profiles(json.loads(raw))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self.send_error(400)
                return
            for record in records:
                # Não registra números, conteúdo das mensagens ou payload completo.
                print(json.dumps({"profile_name": record["profile_name"], "status": record["status"]}, ensure_ascii=False), flush=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, *_args):
            # Não registrar tokens ou informações pessoais no URL.
            pass

    print(f"Webhook local: http://{host}:{port}/webhook. HTTPS público é obrigatório na Meta.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Nomes de perfil de mensagens WhatsApp Business recebidas")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="Evento fictício")
    group.add_argument("--file", type=Path, help="JSON local NÃO autenticado")
    group.add_argument("--serve", action="store_true", help="Receber webhook assinado")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if args.serve:
        serve(args.host, args.port)
        return
    try:
        payload = example_payload() if args.demo else json.loads(args.file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "verified_meta_signature": False,
        "profiles": extract_profiles(payload),
        "note": "Modo local ou fictício: os dados podem ser fabricados e não confirmam identidade.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
