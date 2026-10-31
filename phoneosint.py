"""PhoneOSINT: validacao e identificacao empresarial baseada em evidencias locais.

Nao consulta cadastros privados, nao realiza scraping e nao valida titulares.
"""
import argparse
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import geocoder, PhoneNumberFormat, PhoneNumberType

PORTAL = "https://www.qualempresameligou.com.br/"


def normalize_number(raw: str) -> dict:
    """Valida numero BR e devolve metadados nao pessoais."""
    try:
        p = phonenumbers.parse(raw, "BR")
    except phonenumbers.NumberParseException as exc:
        raise ValueError("Numero invalido") from exc
    if p.country_code != 55 or not phonenumbers.is_valid_number(p):
        raise ValueError("Informe um numero brasileiro valido.")
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
    """Retorna somente alegacoes empresariais com fonte HTTPS e data valida.

    A evidencia nao e verificada automaticamente; verificar manualmente
    a correspondencia exata com a fonte original.
    """
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("kind") != "company_public" or record.get("number") != number:
            continue
        source = record.get("source_url", "")
        url = urlparse(source)
        try:
            checked = date.fromisoformat(record.get("checked_on", ""))
        except ValueError:
            continue
        if (url.scheme != "https" or not url.netloc or checked > date.today()
                or not isinstance(record.get("name"), str)
                or not record["name"].strip()):
            continue
        return {
            "name": record["name"].strip(),
            "source": source,
            "checked_on": checked.isoformat(),
            "status": "nome empresarial informado por evidencia (nao verificado automaticamente)",
        }
    return None


def analyze(raw: str, records: list | None = None) -> dict:
    result = normalize_number(raw)
    evidence = name_from_public_business_evidence(result["number"], records or [])
    result.update({
        "company_name": evidence["name"] if evidence else None,
        "status": evidence["status"] if evidence else "Titular nao identificado",
        "evidence": evidence,
        "official_business_lookup": PORTAL,
        "warning": "Nome empresarial nao comprova usuario atual do WhatsApp nem titular de pessoa fisica.",
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="OSINT legal de numeros BR")
    parser.add_argument("number", help="Numero com DDD, preferencialmente +55")
    parser.add_argument("--evidence", type=Path, help="JSON local de evidencias empresariais")
    args = parser.parse_args()
    records = []
    if args.evidence:
        try:
            records = json.loads(args.evidence.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                parser.error("O arquivo de evidencia deve conter uma lista JSON.")
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"Nao foi possivel ler as evidencias: {exc}")
    try:
        result = analyze(args.number, records)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
