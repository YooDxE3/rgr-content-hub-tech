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

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não está definida.")

# =========================
# FUNÇÃO: DESCOBRIR MODELO VÁLIDO (AUTO-FIX)
# =========================
def get_working_model_url():
    """
    Consulta a API para listar os modelos disponíveis para esta chave
    e retorna a URL do primeiro que servir.
    """
    print("🔍 Buscando modelos disponíveis para sua chave...")
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(list_url)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Erro ao listar modelos: {data['error']['message']}")
            return None

        # Procura um modelo que seja 'Gemini' e suporte 'generateContent'
        for model in data.get('models', []):
            name = model.get('name', '')
            methods = model.get('supportedGenerationMethods', [])
            
            if 'generateContent' in methods and 'gemini' in name.lower():
                # Preferência por modelos Flash ou Pro (mais rápidos/estáveis)
                if 'flash' in name or 'pro' in name:
                    print(f"✅ Modelo encontrado e selecionado: {name}")
                    # O 'name' já vem no formato 'models/gemini-xyz'
                    return f"https://generativelanguage.googleapis.com/v1beta/{name}:generateContent?key={API_KEY}"
        
        # Se não achou preferidos, pega o primeiro que aparecer
        if data.get('models'):
            fallback = data['models'][0]['name']
            print(f"⚠️ Usando modelo de fallback: {fallback}")
            return f"https://generativelanguage.googleapis.com/v1beta/{fallback}:generateContent?key={API_KEY}"
            
    except Exception as e:
        print(f"Erro na conexão de listagem: {e}")
    
    return None

# =========================
# FUNÇÕES DE GERAÇÃO
# =========================

def excerpt_from_html(html: str, limit: int = 160) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    return text[:limit].rstrip() + "..."

def generate_health_tips():
    # Passo 1: Descobre a URL correta dinamicamente
    api_url = get_working_model_url()
    
    if not api_url:
        print("❌ Nenhum modelo compatível encontrado. Verifique se a API 'Generative Language' está ativada no Google Cloud.")
        return []

    prompt_text = """
    Você é um assistente de saúde corporativa da RGR Saúde.
    Gere 3 dicas de saúde e bem-estar para o ambiente de trabalho.
    
    REGRAS OBRIGATÓRIAS:
    1. A resposta deve ser APENAS um JSON puro. SEM markdown.
    2. Estrutura: Lista de objetos.
    3. Cada objeto: "id", "tags" (3 tags), "content" (pt, en, es).
    4. "content" deve ter "title" e "html" (tags <p>).

    Exemplo JSON:
    [
      { "id": "ex", "tags": ["a","b"], "content": { "pt": { "title": "...", "html": "..." }, "en": {...}, "es": {...} } }
    ]
    """

    payload = {
        "contents": [{ "parts": [{"text": prompt_text}] }],
        "generationConfig": { "responseMimeType": "application/json" }
    }

    try:
        response = requests.post(api_url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"ERRO API ({response.status_code}): {response.text}")
            return []
        
        result = response.json()
        text_content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Limpeza de segurança
        text_content = text_content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text_content)

    except Exception as e:
        print(f"Erro na execução: {e}")
        return []

# =========================
# FLUXO PRINCIPAL
# =========================

print("🤖 Iniciando robô de conteúdo...")
health_tips_data = generate_health_tips()

if not health_tips_data:
    print("⚠️ Falha na geração. Abortando.")
    exit(1)

now = datetime.utcnow().isoformat()

feed = {
    "generated_at": now,
    "posts": []
}

for item in health_tips_data:
    base_id = item.get("id", "post")
    tags = item.get("tags", ["saúde"])
    
    for lang in ["pt", "en", "es"]:
        content_data = item.get("content", {}).get(lang)
        if content_data:
            post_id = f"{base_id}-{lang}"
            feed["posts"].append({
                "id": post_id,
                "category": CATEGORY,
                "lang": lang,
                "title": content_data["title"],
                "excerpt": excerpt_from_html(content_data["html"]),
                "content": content_data["html"],
                "tags": tags,
                "published_at": now,
                "author": AUTHOR
            })

with open(FEED_PATH, "w", encoding="utf-8") as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

print(f"✅ Feed gerado com sucesso: {len(feed['posts'])} posts criados via IA.")
