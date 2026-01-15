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
# DICAS DE SAÚDE (MULTILÍNGUE)
# =========================

# Estrutura: ID único + Traduções
health_tips_data = [
    {
        "id": "water",
        "tags": ["hidratação", "hydration", "saúde", "health"],
        "content": {
            "pt": {
                "title": "A importância de beber água todos os dias",
                "html": (
                    "<p>Manter o corpo hidratado é essencial para o bom funcionamento do organismo.</p>"
                    "<p>A água auxilia na digestão, circulação e controle da temperatura.</p>"
                )
            },
            "en": {
                "title": "The importance of drinking water every day",
                "html": (
                    "<p>Keeping the body hydrated is essential for the proper functioning of the organism.</p>"
                    "<p>Water aids in digestion, circulation, and temperature control.</p>"
                )
            },
            "es": {
                "title": "La importancia de beber agua todos los días",
                "html": (
                    "<p>Mantener el cuerpo hidratado es esencial para el buen funcionamiento del organismo.</p>"
                    "<p>El agua ayuda en la digestión, la circulación y el control de la temperatura.</p>"
                )
            }
        }
    },
    {
        "id": "sleep",
        "tags": ["sono", "sleep", "sueño", "bem-estar"],
        "content": {
            "pt": {
                "title": "Por que dormir bem melhora sua saúde",
                "html": (
                    "<p>Uma boa noite de sono é fundamental para a recuperação física e mental.</p>"
                    "<p>Dormir mal pode afetar o sistema imunológico e a memória.</p>"
                )
            },
            "en": {
                "title": "Why sleeping well improves your health",
                "html": (
                    "<p>A good night's sleep is fundamental for physical and mental recovery.</p>"
                    "<p>Poor sleep can affect the immune system and memory.</p>"
                )
            },
            "es": {
                "title": "Por qué dormir bien mejora tu salud",
                "html": (
                    "<p>Una buena noche de sueño es fundamental para la recuperación física y mental.</p>"
                    "<p>Dormir mal puede afectar el sistema inmunológico y la memoria.</p>"
                )
            }
        }
    },
    {
        "id": "food",
        "tags": ["nutrição", "nutrition", "alimentación"],
        "content": {
            "pt": {
                "title": "Alimentação equilibrada faz diferença",
                "html": (
                    "<p>Uma alimentação balanceada fornece os nutrientes necessários para o corpo.</p>"
                    "<p>Evitar ultraprocessados e priorizar alimentos naturais melhora a disposição.</p>"
                )
            },
            "en": {
                "title": "Balanced diet makes a difference",
                "html": (
                    "<p>A balanced diet provides the necessary nutrients for the body.</p>"
                    "<p>Avoiding ultra-processed foods improves energy levels.</p>"
                )
            },
            "es": {
                "title": "Una alimentación equilibrada marca la diferencia",
                "html": (
                    "<p>Una alimentación equilibrada proporciona los nutrientes necesarios para el cuerpo.</p>"
                    "<p>Evitar los ultraprocesados mejora la disposición.</p>"
                )
            }
        }
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

# Loop pelos dados e pelas línguas
for item in health_tips_data:
    base_id = item["id"]
    tags = item["tags"]
    
    for lang in ["pt", "en", "es"]:
        data = item["content"].get(lang)
        
        if data:
            # Cria um ID único combinando slug + lang (ex: water-en)
            post_id = f"{base_id}-{lang}"
            
            post = {
                "id": post_id,
                "category": CATEGORY,
                "lang": lang, # CAMPO IMPORTANTE PARA O FILTRO NO SITE
                "title": data["title"],
                "excerpt": excerpt_from_html(data["html"]),
                "content": data["html"],
                "tags": tags,
                "published_at": now,
                "author": AUTHOR
            }

            feed["posts"].append(post)

# =========================
# SALVA O ARQUIVO
# =========================

with open(FEED_PATH, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print(f"✅ Feed gerado com {len(feed['posts'])} posts (PT/EN/ES)")
