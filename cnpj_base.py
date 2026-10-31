"""Importador OFFLINE dos Dados Abertos do CNPJ da Receita Federal.

Não baixa arquivos, não acessa serviços externos, não identifica pessoas físicas.
Aceita Empresas e Estabelecimentos (CSV ou ZIP, formato sem cabeçalho, ; e Latin-1).
"""
from contextlib import contextmanager
import argparse
import csv
from datetime import date, datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import sqlite3
from zipfile import ZipFile

SOURCE = "https://dadosabertos.rfb.gov.br/CNPJ/"
LAYOUT = "https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf"
# Sociedades com nome empresarial próprio. NÃO inclui empresários individuais/MEI.
ALLOWED_NATURES = {"2046", "2054", "2062"}
SCHEMA_VERSION = 1


@contextmanager
def csv_rows(path: Path):
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            files = [n for n in archive.namelist() if not n.endswith("/") and not n.startswith("__MACOSX/")]
            if len(files) != 1:
                raise ValueError(f"ZIP deve conter um único arquivo de dados: {path.name}")
            with archive.open(files[0]) as binary:
                with io.TextIOWrapper(binary, encoding="latin-1", newline="") as stream:
                    yield csv.reader(stream, delimiter=";", quotechar='"')
    else:
        with path.open("r", encoding="latin-1", newline="") as stream:
            yield csv.reader(stream, delimiter=";", quotechar='"')


def public_phone(ddd: str, subscriber: str) -> str | None:
    """Só normaliza padrão de DDD+telefone; cadastro não garante uso atual."""
    area = re.sub(r"[\s()\-]", "", ddd)
    local = re.sub(r"[\s()\-]", "", subscriber)
    if (not re.fullmatch(r"\d{2}", area)
            or not re.fullmatch(r"\d{8,9}", local)
            or area[0] == "0" or len(set(local)) == 1):
        return None
    return "+55" + area + local


def _flush_companies(con, batch):
    con.executemany("INSERT OR IGNORE INTO companies(base,name) VALUES(?,?)", batch)
    batch.clear()


def _flush_numbers(con, batch):
    # Junta em lotes pequenos, sem manter telefone associado a nome pessoal.
    con.executemany("INSERT INTO staging(base,cnpj,phone) VALUES(?,?,?)", batch)
    con.execute("""INSERT OR IGNORE INTO phone_records(phone,cnpj,name)
                   SELECT s.phone,s.cnpj,c.name FROM staging s
                   JOIN companies c ON c.base=s.base""")
    con.execute("DELETE FROM staging")
    batch.clear()


def import_cnpj(empresas: Path, estabelecimentos: Path, db: Path, snapshot: str) -> dict:
    """Gera índice SQLite LOCAL. Exige ambos arquivos da mesma extração."""
    dt = date.fromisoformat(snapshot)
    if dt > date.today():
        raise ValueError("Data do arquivo não pode ser futura")
    if db.exists():
        raise FileExistsError("Banco já existe; escolha outro caminho para não sobrescrever dados")
    if not empresas.is_file() or not estabelecimentos.is_file():
        raise FileNotFoundError("Informe dois arquivos existentes: Empresas e Estabelecimentos")
    db.parent.mkdir(parents=True, exist_ok=True)
    tmp = db.with_name(db.name + ".tmp")
    if tmp.exists():
        raise FileExistsError("Arquivo temporário já existe: " + str(tmp))
    count_companies = 0
    count_numbers = 0
    con = sqlite3.connect(tmp)
    try:
        con.execute("CREATE TABLE companies(base TEXT PRIMARY KEY, name TEXT NOT NULL)")
        con.execute("CREATE TABLE phone_records(phone TEXT NOT NULL, cnpj TEXT NOT NULL, name TEXT NOT NULL, UNIQUE(phone,cnpj))")
        con.execute("CREATE TEMP TABLE staging(base TEXT, cnpj TEXT, phone TEXT)")
        companies = []
        with csv_rows(empresas) as rows:
            for row in rows:
                if len(row) < 3 or row[2].strip() not in ALLOWED_NATURES:
                    continue
                base, name = row[0].strip(), row[1].strip()
                if not re.fullmatch(r"\d{8}", base) or not name:
                    continue
                companies.append((base, name))
                count_companies += 1
                if len(companies) >= 2000:
                    _flush_companies(con, companies)
        if companies:
            _flush_companies(con, companies)
        con.commit()
        numbers = []
        with csv_rows(estabelecimentos) as rows:
            for row in rows:
                # Índices oficiais: 0=base 1=ordem 2=dv 5=situação 21/22 e 23/24=telefone
                if len(row) < 25 or row[5].strip().zfill(2) != "02":
                    continue
                base, order, dv = (row[0].strip(), row[1].strip(), row[2].strip())
                if not (re.fullmatch(r"\d{8}", base)
                        and re.fullmatch(r"\d{4}", order)
                        and re.fullmatch(r"\d{2}", dv)):
                    continue
                cnpj = base + order + dv
                phones = {public_phone(row[21], row[22]), public_phone(row[23], row[24])} - {None}
                for phone in phones:
                    numbers.append((base, cnpj, phone))
                    count_numbers += 1
                    if len(numbers) >= 2000:
                        _flush_numbers(con, numbers)
        if numbers:
            _flush_numbers(con, numbers)
        con.commit()
        con.execute("DROP TABLE companies")
        con.execute("CREATE INDEX idx_phone ON phone_records(phone)")
        con.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.executemany("INSERT INTO metadata(key,value) VALUES(?,?)", [
            ("schema_version", str(SCHEMA_VERSION)),
            ("snapshot", snapshot),
            ("source_url", SOURCE),
            ("origin_note", "Fontes declaradas pelo importador; arquivos não autenticados automaticamente"),
            ("imported_at", datetime.now(timezone.utc).isoformat()),
        ])
        total = con.execute("SELECT COUNT(*) FROM phone_records").fetchone()[0]
        con.commit()
        con.close()
        os.replace(tmp, db)
        return {"companies_eligible": count_companies, "numbers_read": count_numbers,
                "associations_indexed": total, "snapshot": snapshot,
                "note": "Associação cadastral histórica, não comprova titular atual da linha"}
    except Exception:
        con.close()
        if tmp.exists():
            tmp.unlink()
        raise


def lookup_cnpj(number: str, db: Path) -> dict:
    """Consulta exata; retorna todas as associações até 20 com alerta de ambiguidade."""
    if not db.is_file():
        raise FileNotFoundError("Banco local não encontrado: " + str(db))
    uri = db.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        meta = dict(con.execute("SELECT key,value FROM metadata"))
        if meta.get("schema_version") != str(SCHEMA_VERSION):
            raise ValueError("Versão de banco incompatível")
        rows = con.execute("SELECT DISTINCT cnpj,name FROM phone_records WHERE phone=? ORDER BY cnpj LIMIT 21", (number,)).fetchall()
    matches = [{"cnpj": cnpj, "name": name} for cnpj, name in rows[:20]]
    return {"matches": matches, "more_results": len(rows) > 20,
            "snapshot": meta.get("snapshot"), "source": meta.get("source_url"),
            "origin_note": meta.get("origin_note"),
            "warning": "Nome empresarial vinculado ao telefone no CNPJ histórico, sem confirmar titularidade da linha ou WhatsApp."}


def main():
    p = argparse.ArgumentParser(description="Importar CSV/ZIP públicos de CNPJ offline")
    p.add_argument("--empresas", type=Path, required=True)
    p.add_argument("--estabelecimentos", type=Path, required=True)
    p.add_argument("--snapshot", required=True, help="Data de extração YYYY-MM-DD")
    p.add_argument("--db", type=Path, default=Path("phoneosint_cnpj.sqlite"))
    args = p.parse_args()
    try:
        result = import_cnpj(args.empresas, args.estabelecimentos, args.db, args.snapshot)
    except (ValueError, OSError, sqlite3.Error) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
