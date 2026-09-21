import os
import time
import requests

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

# Headers padrão para a API
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def baixar_pdf_proposicao(id_proposicao):
    url_detalhe = f"{BASE_URL}/proposicoes/{id_proposicao}"
    
    print(f"Consultando detalhes da proposição ID {id_proposicao}...")
    response = requests.get(url_detalhe, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Erro ao buscar proposição: HTTP {response.status_code}")
        return
    
    dados = response.json().get("dados", {})
    sigla = dados.get("siglaTipo")
    numero = dados.get("numero")
    ano = dados.get("ano")
    url_pdf = dados.get("urlInteiroTeor")
    
    print(f"Proposição encontrada: {sigla} {numero}/{ano}")
    print(f"URL do Inteiro Teor (PDF): {url_pdf}")
    
    if not url_pdf:
        print("Aviso: Esta proposição não possui 'urlInteiroTeor' preenchido.")
        return

    pdf_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.camara.leg.br/",
        "Connection": "keep-alive"
    }

    print("Aguardando 1 segundo para respeitar o rate limit...")
    time.sleep(1)

    print("Baixando o arquivo PDF...")
    pdf_resp = requests.get(url_pdf, headers=pdf_headers, stream=True)
    
    print(f"Status HTTP do PDF: {pdf_resp.status_code}")
    print(f"Content-Type: {pdf_resp.headers.get('Content-Type')}")

    if pdf_resp.status_code == 200:
        nome_arquivo = f"proposicao_{sigla}_{numero}_{ano}.pdf".replace("/", "_")
        
        with open(nome_arquivo, "wb") as f:
            for chunk in pdf_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        tamanho_kb = os.path.getsize(nome_arquivo) / 1024
        print(f"Sucesso! PDF salvo como: '{nome_arquivo}' ({tamanho_kb:.2f} KB)")
    else:
        print(f"Falha ao baixar o PDF. Status HTTP: {pdf_resp.status_code}")
        print(f"Retorno do servidor: {pdf_resp.text[:150]}")

if __name__ == "__main__":
    ID_TESTE = 2646600
    baixar_pdf_proposicao(ID_TESTE)