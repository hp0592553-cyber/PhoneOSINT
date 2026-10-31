"""Simulacao offline de cruzamento de cadastros usando apenas registros sinteticos.

Nao consulta vazamentos, Telegram, bancos privados, CPF ou servicos externos.
"""
import json

RECORDS = [
    {"source": "cadastro_ficticio_A", "record_key": "DEMO-001",
     "name": "PESSOA FICTICIA ALFA", "city": "CIDADE EXEMPLO",
     "updated": "2024-01-01", "kind": "demonstracao"},
    {"source": "cadastro_ficticio_B", "record_key": "DEMO-001",
     "name": "PESSOA FICTICIA ALFA", "city": "CIDADE EXEMPLO",
     "updated": "2025-05-01", "kind": "demonstracao"},
    {"source": "cadastro_ficticio_C", "record_key": "DEMO-001",
     "name": "PESSOA FICTICIA BETA", "city": "OUTRA CIDADE",
     "updated": "2022-02-01", "kind": "demonstracao"},
]


def demo_report():
    records = [r for r in RECORDS if r["record_key"] == "DEMO-001"]
    names = sorted({r["name"] for r in records})
    return {
        "mode": "SIMULACAO - NENHUM DADO REAL",
        "test_record": "DEMO-001",
        "matches": len(records),
        "sources": sorted({r["source"] for r in records}),
        "names": names,
        "conflicting_names": len(names) > 1,
        "latest_source_date": max(r["updated"] for r in records),
        "identity_confirmed": False,
        "warning": "Demonstra como bots misturam fontes antigas; nomes e locais sao inventados.",
    }


if __name__ == "__main__":
    print(json.dumps(demo_report(), indent=2, ensure_ascii=False))
