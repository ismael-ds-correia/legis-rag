import os
import time
import requests
from pathlib import Path
import json
from tqdm import tqdm

# Configurações
BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
ANUAL_URL = "http://dadosabertos.camara.leg.br/arquivos/proposicoes/json"
RAW_DIR = Path("data/raw")
JSON_DIR = RAW_DIR / "json"
PDF_DIR = RAW_DIR / "pdfs"

# Headers para simular navegador
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

PDF_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.camara.leg.br/",
    "Connection": "keep-alive"
}

def create_directories():
    """Cria as pastas necessárias para armazenar os dados."""
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

def download_annual_json(year):
    """Baixa o arquivo JSON anual de proposições."""
    url = f"{ANUAL_URL}/proposicoes-{year}.json"
    local_path = JSON_DIR / f"proposicoes-{year}.json"
    
    print(f"Baixando JSON de {year} de {url}...")
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        local_path.write_bytes(response.content)
        print(f"Salvo: {local_path}")
        return local_path
    else:
        print(f"Erro ao baixar JSON de {year}: HTTP {response.status_code}")
        return None

def download_pdf(proposicao):
    """Baixa o PDF de uma proposição específica."""
    sigla = proposicao.get("siglaTipo")
    numero = proposicao.get("numero")
    ano = proposicao.get("ano")
    url_pdf = proposicao.get("urlInteiroTeor")
    
    if not url_pdf:
        print(f"  - {sigla} {numero}/{ano}: sem URL de PDF")
        return False
    
    # Respeitar rate limit
    #time.sleep(1)
    
    filename = f"proposicao_{sigla}_{numero}_{ano}.pdf".replace("/", "_")
    local_path = PDF_DIR / filename
    
    # Pular se já existe
    if local_path.exists():
        print(f"  - {sigla} {numero}/{ano}: já existe")
        return True
    
    print(f"  - {sigla} {numero}/{ano}: baixando...")
    
    try:
        response = requests.get(url_pdf, headers=PDF_HEADERS, stream=True)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"    Salvo: {filename}")
            return True
        else:
            print(f"    Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"    Erro: {e}")
        return False

def process_json_file(json_path):
    """Processa um arquivo JSON de proposições e baixa os PDFs."""
    print(f"\nProcessando {json_path}...")
    
    data = json.loads(json_path.read_text())
    proposicoes = data.get("dados", [])
    
    # Filtrar apenas PL, PLP e PEC
    tipos_desejados = {"PL", "PLP", "PEC"}
    proposicoes_filtradas = [p for p in proposicoes if p.get("siglaTipo") in tipos_desejados]
    
    print(f"Total de proposições: {len(proposicoes)}")
    print(f"Proposições filtradas (PL, PLP, PEC): {len(proposicoes_filtradas)}")
    
    sucesso = 0
    falha = 0
    
    # Barra de progresso
    for prop in tqdm(proposicoes_filtradas, desc="Baixando PDFs", unit="prop"):
        if download_pdf(prop):
            sucesso += 1
        else:
            falha += 1
    
    print(f"\nResumo: {sucesso} PDFs baixados, {falha} falhas")

def main():
    """Executa o pipeline de extração."""
    create_directories()
    
    # Baixar JSONs de 2026
    for year in [2025, 2026]:
        json_path = download_annual_json(year)
        if json_path:
            process_json_file(json_path)

if __name__ == "__main__":
    main()