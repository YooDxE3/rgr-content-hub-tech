import json
import datetime
from pathlib import Path

OUT = Path("output")
OUT.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    # Exemplo B2B (você pode evoluir com IA depois)
    feed = {
        "updated_at": now_iso(),
        "items": [
            {
                "category": "Governança",
                "title": "SLA não é slogan: é métrica",
                "summary": "SLA só existe quando você mede. Checklist executivo: definição, gatilhos e auditoria."
            },
            {
                "category": "Operação",
                "title": "Escala D-5: o ritual que evita crise",
                "summary": "Padronize a confirmação com antecedência, banco e reposição com KPI de tempo."
            },
            {
                "category": "Qualidade",
                "title": "Contingência em 2h: estrutura real",
                "summary": "Plano testável: acionamento, regulação, substituição e lições aprendidas."
            }
        ]
    }

    (OUT / "site_feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: gerado output/site_feed.json")

if __name__ == "__main__":
    main()
