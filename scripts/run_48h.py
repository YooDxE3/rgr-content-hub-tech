import json
import os
import requests
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

# Pega a chave dos Segredos
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está definida.")

# URL direta da API do Google (v1beta) - Modelo Gemini 1.5 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# =========================
# FUNÇÕES AUXILIARES
# =========================

def excerpt_from_html(html: str, limit: int = 160) -> str:
    # Remove tags HTML para criar o resumo
    text = re.sub(r"<[^>]+>", "", html)
    return text[:limit].rstrip() + "..."

def generate_health_tips():
    """
    Usa a API REST do Gemini para gerar 3 dicas de saúde estruturadas.
    """
    
    prompt_text = """
    Você é um assistente de saúde corporativa da RGR Saúde.
    Gere 3 dicas de saúde e bem-estar para o ambiente de trabalho.
    
    REGRAS OBRIGATÓRIAS:
    1. A resposta deve ser APENAS um JSON puro. Não use blocos de código markdown (```json).
    2. A estrutura deve ser uma lista de objetos.
    3. Cada objeto deve ter:
       - "id": string curta em inglês (ex: "ergonomics")
       - "tags": lista com 3 tags (ex: ["saúde", "health", "ergonomia"])
       - "content": objeto com as chaves "pt", "en", "es".
       - Dentro de cada língua: "title" e "html" (com tags <p>).

    Exemplo de JSON de retorno:
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

    # Monta o corpo da requisição HTTP
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        # Faz a chamada POST direta
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status() # Levanta erro se não for 200 OK
        
        result = response.json()
        
        # Extrai o texto da resposta
        text_content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Limpa possíveis formatações markdown que a IA coloque por teimosia
        text_content = text_content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text_content)

    except Exception as e:
        print(f"Erro na requisição para o Google: {e}")
        if 'response' in locals():
            print(f"Detalhe do erro: {response.text}")
        return []

# =========================
# GERAÇÃO DO FEED
# =========================

print("🤖 Solicitando dicas para o Gemini (via REST API)...")
health_tips_data = generate_health_tips()

if not health_tips_data:
    print("⚠️ Nenhuma dica gerada ou erro na API. Abortando.")
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
