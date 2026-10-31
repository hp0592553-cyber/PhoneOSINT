"""Consulta local de evidências autorizadas; nenhuma requisição de rede."""
import argparse
from datetime import date
import json
import os
from pathlib import Path

from phoneosint import normalize_number

SOURCES = {
    "truecaller": "https://www.truecaller.com/reverse-phone-number-lookup",
    "sync_me": "https://sync.me/pt-br/reverse-phone-lookup/",
}
STATUS = "nome associado, não verificado"


def load_evidence(path):
    try:
        if path.stat().st_size > 1024 * 1024:
            raise ValueError
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError
        return records
    except (OSError, ValueError, UnicodeError):
        # Não expor caminho, conteúdo pessoal ou mensagens de exceção.
        raise ValueError("Falha ao ler evidências locais; confira arquivo e lista JSON.") from None


def associated_names(raw, records=()):
    details = normalize_number(raw)
    matches = []
    rejected = 0
    for record in records:
        try:
            if not isinstance(record, dict):
                raise ValueError
            if normalize_number(record.get("number", ""))["number"] != details["number"]:
                continue
            if record.get("authorized") is not True:
                raise ValueError
            source = record.get("source")
            if source not in SOURCES:
                raise ValueError
            name = record.get("name")
            if (not isinstance(name, str) or not name.strip() or len(name) > 200
                    or any(ord(c) < 32 or ord(c) == 127 for c in name)):
                raise ValueError
            checked = date.fromisoformat(record.get("checked_on", ""))
            if checked > date.today():
                raise ValueError
            item = {"name": name.strip(), "source": source,
                    "source_url": SOURCES[source], "checked_on": checked.isoformat(),
                    "status": STATUS}
            if item not in matches:
                matches.append(item)
        except (ValueError, TypeError, AttributeError):
            rejected += 1
    return {
        "number": "omitido",
        "valid_format": True,
        "line_type": details["type"],
        "names": matches,
        "conflicting_names": len({m["name"].casefold() for m in matches}) > 1,
        "rejected_records": rejected,
        "status": STATUS if matches else "Nenhum nome encontrado nas evidências locais",
        "automatic_lookup": "não executado; sem API autorizada sem chave implementada",
        "warning": "Não comprova nome atual do WhatsApp, posse da linha ou titularidade na operadora.",
    }


def basic_report(raw):
    result = associated_names(raw)
    return "\n".join([
        "## PhoneOSINT — Nome por número (consulta autorizada)", "",
        "- Número: formato brasileiro válido; número completo omitido.",
        "- Validação de formato não confirma linha ativa ou posse.",
        "- Nome associado: NÃO IDENTIFICADO por esta execução; nenhuma base de nomes foi consultada.",
        "- Titular cadastral: não identificado.", "",
        "### Onde pesquisar o nome associado ao número",
        *[f"- {source}: {url}" for source, url in SOURCES.items()],
        "Abra a página, selecione Brasil (+55) e digite seu número diretamente no site.",
        "Login, assinatura, disponibilidade e limites dependem do serviço; respeite seus termos.",
        "Não há link com número: URL de busca oficialmente documentada não foi verificada.",
        "Registre eventual resultado somente em arquivo local *.evidence.json, nunca nos inputs.",
        result["warning"], "",
        "Inputs workflow_dispatch não são secretos. Prefira secrets.PHONE_NUMBER e deixe numero vazio.",
        "Este workflow valida número e indica ferramentas manuais; não acessa nomes de terceiros, WhatsApp ou cadastros privados.", "",
    ])


def workflow_main():
    if os.environ.get("AUTHORIZED", "").lower() != "true":
        raise SystemExit("Confirme que o número é seu ou que possui autorização.")
    raw = os.environ.get("PHONE_SECRET", "").strip() or os.environ.get("PHONE_INPUT", "").strip()
    if not raw:
        raise SystemExit("Configure PHONE_NUMBER ou informe numero (campo não secreto).")
    try:
        report = basic_report(raw)
    except (ValueError, TypeError):
        raise SystemExit("Número brasileiro inválido. Confira DDD e dígitos.") from None
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(report)


def main():
    parser = argparse.ArgumentParser(description="Nomes associados por evidência local autorizada")
    parser.add_argument("--evidence", type=Path, required=True, help="Arquivo local *.evidence.json")
    args = parser.parse_args()
    # Evita número no histórico de comandos; não registra a entrada no terminal.
    from getpass import getpass
    raw = getpass("Seu número brasileiro com DDD (entrada oculta): ")
    try:
        result = associated_names(raw, load_evidence(args.evidence))
    except (ValueError, TypeError):
        parser.error("Número inválido ou falha ao ler evidências locais.")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
