import json
from datetime import datetime
import unicodedata
import re
from pathlib import Path

# =========================
# CONFIGURAÇÕES
# =========================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FEED_PATH = OUTPUT_DIR / "site_feed.json"

AUTHOR = "RGR Saúde"
CATEGORY = "saude"

# =========================
# FUNÇÕES AUXILIARES
# =========================

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")

def excerpt_from_html(html: str, limit: int = 160) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    return text[:limit].rstrip()

# =========================
# DICAS DE SAÚDE
# =========================

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

# =========================
# GERAÇÃO DO FEED
# =========================

now = datetime.utcnow().isoformat()

feed = {
    "generated_at": now,
    "posts": []
}

for tip in health_tips:
    slug = slugify(tip["title"])

    post = {
        "id": slug,
        "category": CATEGORY,
        "title": tip["title"],
        "excerpt": excerpt_from_html(tip["content"]),
        "content": tip["content"],
        "tags": tip["tags"],
        "published_at": now,
        "author": AUTHOR
    }

    feed["posts"].append(post)

# =========================
# SALVA O ARQUIVO
# =========================

with open(FEED_PATH, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print("✅ Feed de dicas de saúde gerado com sucesso")
