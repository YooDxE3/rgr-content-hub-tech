import json
import os
from google import genai
from google.genai import types
from datetime import datetime
import re
from pathlib import Path

# =========================
# CONFIGURAÇÕES
# =========================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FEED_PATH = OUTPUT_DIR / "site_feed.json"

AUTHOR = "RGR Saúde (IA)"
CATEGORY = "saude"

# Configura a API do Gemini (Nova Biblioteca)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está definida.")

client = genai.Client(api_key=API_KEY)

# =========================
# FUNÇÕES AUXILIARES
# =========================

def excerpt_from_html(html: str, limit: int = 160) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    return text[:limit].rstrip() + "..."

def generate_health_tips():
    """
    Usa o Gemini (via google-genai) para gerar 3 dicas de saúde estruturadas.
    """
    
    prompt = """
    Você é um assistente de saúde corporativa da RGR Saúde.
    Gere 3 dicas de saúde e bem-estar para o ambiente de trabalho.
    
    REGRAS:
    1. Retorne APENAS um JSON válido.
    2. A estrutura deve ser uma lista de objetos.
    3. Cada objeto deve ter:
       - "id": uma string curta em inglês (ex: "ergonomics-tips")
       - "tags": lista com 3 tags misturando pt/en (ex: ["saúde", "health", "ergonomia"])
       - "content": um objeto com as chaves "pt", "en", "es".
       - Dentro de cada língua, deve ter "title" e "html".
       - O "html" deve conter 2 ou 3 parágrafos curtos dentro de tags <p>.

    Exemplo de estrutura desejada:
    [
      {
        "id": "exemplo",
        "tags": ["tag1", "tag2"],
        "content": {
          "pt": { "title": "Título PT", "html": "<p>Texto PT</p>" },
          "en": { "title": "Title EN", "html": "<p>Text EN</p>" },
          "es": { "title": "Título ES", "html": "<p>Texto ES</p>" }
        }
      }
    ]
    """

    try:
        # Chamada atualizada para a nova biblioteca
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro ao gerar conteúdo com IA: {e}")
        return []

# =========================
# GERAÇÃO DO FEED
# =========================

print("🤖 Solicitando dicas para o Gemini (via google-genai)...")
health_tips_data = generate_health_tips()

if not health_tips_data:
    print("⚠️ Nenhuma dica gerada. Abortando.")
    exit(1)

now = datetime.utcnow().isoformat()

feed = {
    "generated_at": now,
    "posts": []
}

# Processa os dados retornados pela IA
for item in health_tips_data:
    base_id = item.get("id", "post")
    tags = item.get("tags", ["saúde"])
    
    # Loop pelas línguas para criar os posts individuais
    for lang in ["pt", "en", "es"]:
        content_data = item.get("content", {}).get(lang)
        
        if content_data:
            post_id = f"{base_id}-{lang}"
            
            post = {
                "id": post_id,
                "category": CATEGORY,
                "lang": lang,
                "title": content_data["title"],
                "excerpt": excerpt_from_html(content_data["html"]),
                "content": content_data["html"],
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

print(f"✅ Feed gerado com sucesso: {len(feed['posts'])} posts criados via IA.")
