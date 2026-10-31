"""PhoneOSINT: validação telefônica e consulta LOCAL a dados empresariais públicos.

Não acessa cadastros privados, contas do WhatsApp ou sites automaticamente.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import geocoder, PhoneNumberFormat, PhoneNumberType

from cnpj_base import lookup_cnpj

PORTAL = "https://www.qualempresameligou.com.br/"


def normalize_number(raw: str) -> dict:
    try:
        p = phonenumbers.parse(raw, "BR")
    except phonenumbers.NumberParseException as exc:
        raise ValueError("Número inválido") from exc
    if p.country_code != 55 or not phonenumbers.is_valid_number(p):
        raise ValueError("Informe um número brasileiro válido.")
    e164 = phonenumbers.format_number(p, PhoneNumberFormat.E164)
    kind = phonenumbers.number_type(p)
    return {
        "number": e164,
        "region": geocoder.description_for_number(p, "pt") or "Indeterminada",
        "type": ("celular" if kind == PhoneNumberType.MOBILE
                 else "fixo" if kind == PhoneNumberType.FIXED_LINE
                 else "outro"),
    }


def name_from_public_business_evidence(number: str, records: list) -> dict | None:
    """Evidência empresarial opcional preenchida manualmente, não conferida pela ferramenta."""
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("kind") != "company_public" or record.get("number") != number:
            continue
        source = record.get("source_url", "")
        url = urlparse(source)
        try:
            checked = date.fromisoformat(record.get("checked_on", ""))
        except (TypeError, ValueError):
            continue
        name = record.get("name")
        if (url.scheme != "https" or not url.netloc or checked > date.today()
                or not isinstance(name, str) or not name.strip()):
            continue
        return {
            "name": name.strip(),
            "source": source,
            "checked_on": checked.isoformat(),
            "status": "nome empresarial informado por evidência (não verificado automaticamente)",
        }
    return None


def analyze(raw: str, records: list | None = None, cnpj_db: Path | None = None) -> dict:
    result = normalize_number(raw)
    evidence = name_from_public_business_evidence(result["number"], records or [])
    result.update({
        "company_name": evidence["name"] if evidence else None,
        "status": evidence["status"] if evidence else "Titular não identificado",
        "evidence": evidence,
        "official_business_lookup": PORTAL,
        "warning": "Nome empresarial não comprova usuário atual do WhatsApp nem titular da linha.",
    })
    if cnpj_db is not None:
        lookup = lookup_cnpj(result["number"], cnpj_db)
        result["cnpj_lookup"] = lookup
        matches = lookup["matches"]
        if matches:
            result["company_name"] = matches[0]["name"] if len(matches) == 1 and not lookup["more_results"] else None
            result["status"] = ("Possível vínculo com empresa na base histórica da Receita Federal"
                                if len(matches) == 1 and not lookup["more_results"]
                                else "Múltiplas empresas associadas ao número; titular não identificado")
        elif evidence is None:
            result["status"] = "Sem associação empresarial na base carregada; titular não identificado"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="OSINT legal para telefones brasileiros")
    parser.add_argument("number", help="Número com DDD, preferencialmente +55")
    parser.add_argument("--evidence", type=Path, help="JSON local de evidência empresarial")
    parser.add_argument("--cnpj-db", type=Path, help="Banco SQLite local gerado pelo cnpj_base.py")
    args = parser.parse_args()
    records = []
    if args.evidence:
        try:
            records = json.loads(args.evidence.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                parser.error("O arquivo de evidência deve conter uma lista JSON.")
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"Não foi possível ler as evidências: {exc}")
    try:
        result = analyze(args.number, records, args.cnpj_db)
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
