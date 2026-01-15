import json
import random
from datetime import datetime
import unicodedata
import re
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")

health_tips = [
    {
        "title": "A importância de beber água todos os dias",
        "content": (
            "<p>Manter o corpo hidratado é essencial para o bom funcionamento do organismo.</p>"
            "<p>A água auxilia na digestão, circulação, controle da temperatura corporal e eliminação de toxinas.</p>"
            "<p>O ideal é consumir água ao longo do dia, mesmo sem sentir sede.</p>"
        ),
        "tags": ["hidratação", "saúde", "bem-estar"]
    },
    {
        "title": "Por que dormir bem melhora sua saúde",
        "content": (
            "<p>Uma boa noite de sono é fundamental para a recuperação física e mental.</p>"
            "<p>Dormir mal pode afetar o sistema imunológico, a memória e o humor.</p>"
            "<p>Manter horários regulares para dormir ajuda a melhorar a qualidade do sono.</p>"
        ),
        "tags": ["sono", "qualidade de vida", "saúde"]
    },
    {
        "title": "Alimentação equilibrada faz diferença no dia a dia",
        "content": (
            "<p>Uma alimentação balanceada fornece os nutrientes necessários para o corpo funcionar bem.</p>"
            "<p>Evitar ultraprocessados e priorizar alimentos naturais melhora a disposição.</p>"
            "<p>Pequenas mudanças já trazem grandes benefícios.</p>"
        ),
        "tags": ["alimentação", "nutrição", "saúde"]
    }
]

tip = random.choice(health_tips)
slug = slugify(tip["title"])
now = datetime.utcnow().isoformat()

feed_path = OUTPUT_DIR / "site_feed.json"

if feed_path.exists():
    with open(feed_path, "r", encoding="utf-8") as f:
        feed = json.load(f)
else:
    feed = {
        "generated_at": now,
        "posts": []
    }

post = {
    "id": slug,
    "category": "saude",
    "title": tip["title"],
    "excerpt": tip["content"].split("</p>")[0].replace("<p>", "")[:160],
    "content": tip["content"],
    "tags": tip["tags"],
    "published_at": now,
    "author": "RGR Saúde"
}

# evita duplicar
if not any(p["id"] == post["id"] for p in feed["posts"]):
    feed["posts"].insert(0, post)

with open(feed_path, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print("✅ Dica de saúde gerada com sucesso")
