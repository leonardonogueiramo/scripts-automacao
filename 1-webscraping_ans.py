import os
import requests
import bs4
from bs4 import BeautifulSoup
import zipfile
import re
from urllib.parse import urljoin
import time
import sys

def criar_diretorio(nome_diretorio):
	"""Cria um diretório se ele não existir."""
	if not os.path.exists(nome_diretorio):
		os.makedirs(nome_diretorio)
		print(f"Diretório '{nome_diretorio}' criado com sucesso.")
	else:
		print(f"Diretório '{nome_diretorio}' já existe.")

def baixar_arquivo(url, destino):
	"""Baixa um arquivo da URL especificada e salva no caminho de destino."""
	try:
		resposta = requests.get(url, stream=True)
		resposta.raise_for_status()  # Verifica se houve erro na requisição
		
		with open(destino, 'wb') as arquivo:
			for pedaco in resposta.iter_content(chunk_size=8192):
				arquivo.write(pedaco)
		
		print(f"Arquivo baixado com sucesso: {destino}")
		return True
	except Exception as e:
		print(f"Erro ao baixar o arquivo {url}: {str(e)}")
		return False

def comprimir_arquivos(lista_arquivos, arquivo_zip):
	"""Comprime os arquivos da lista em um único arquivo ZIP."""
	try:
		with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
			for arquivo in lista_arquivos:
				if os.path.exists(arquivo):
					zip_ref.write(arquivo, os.path.basename(arquivo))
					print(f"Arquivo adicionado ao ZIP: {arquivo}")
				else:
					print(f"Arquivo não encontrado: {arquivo}")
		
		print(f"Arquivos compactados com sucesso em: {arquivo_zip}")
		return True
	except Exception as e:
		print(f"Erro ao compactar os arquivos: {str(e)}")
		return False

def buscar_anexos(url):
	"""Busca os links dos anexos I e II no site da ANS."""
	try:
		print(f"Fazendo requisição para {url}")
		resposta = requests.get(url)
		resposta.raise_for_status()
		print(f"Status da resposta: {resposta.status_code}")
		
		# Salvar o HTML para debug
		with open("pagina_ans.html", "w", encoding="utf-8") as f:
			f.write(resposta.text)
		print("HTML da página salvo em 'pagina_ans.html' para debug")
		
		soup = BeautifulSoup(resposta.text, 'html.parser')
		
		# Procurar por links que contenham 'Anexo I' ou 'Anexo II' no texto
		links_anexos = []
		padrao_anexos = re.compile(r'Anexo [I|II]', re.IGNORECASE)
		
		# Estratégia 1: Buscar diretamente pelos anexos
		print("Buscando links por texto...")
		for link in soup.find_all('a'):
			texto_link = link.get_text().strip()
			href = link.get('href')
			
			if href and padrao_anexos.search(texto_link):
				# Converter URL relativa para absoluta
				url_completa = urljoin(url, href)
				links_anexos.append((texto_link, url_completa))
				print(f"Encontrado link para {texto_link}: {url_completa}")
		
		# Estratégia 2: Procurar por links com PDF que contenham as palavras "anexo"
		if not links_anexos:
			print("Buscando por PDFs com 'anexo' no nome...")
			for link in soup.find_all('a'):
				href = link.get('href', '')
				texto_link = link.get_text().strip()
				
				if href.lower().endswith('.pdf') and ('anexo' in href.lower() or 'anexo' in texto_link.lower()):
					url_completa = urljoin(url, href)
					nome_arquivo = os.path.basename(href)
					links_anexos.append((nome_arquivo, url_completa))
					print(f"Encontrado link para PDF: {nome_arquivo}: {url_completa}")
		
		return links_anexos
	except Exception as e:
		print(f"Erro ao buscar anexos: {str(e)}")
		return []

def main():
	print("Iniciando o processo de webscraping...")
	
	# URL do site da ANS
	url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
	print(f"Acessando URL: {url}")
	
	# Diretório para salvar os arquivos
	diretorio_downloads = "downloads_ans"
	criar_diretorio(diretorio_downloads)
	
	# Buscar links dos anexos
	print("Buscando links dos anexos...")
	links_anexos = buscar_anexos(url)
	print(f"Encontrados {len(links_anexos)} links de anexos.")
	
	if not links_anexos:
		print("Não foram encontrados links para os Anexos I e II.")
		return
	
	# Lista para armazenar os caminhos dos arquivos baixados
	arquivos_baixados = []
	
	# Baixar os anexos
	for nome, url_anexo in links_anexos:
		# Criar nome do arquivo baseado no texto do link
		nome_arquivo = f"{nome.replace(' ', '_')}.pdf"
		caminho_arquivo = os.path.join(diretorio_downloads, nome_arquivo)
		
		# Baixar o arquivo
		if baixar_arquivo(url_anexo, caminho_arquivo):
			arquivos_baixados.append(caminho_arquivo)
	
	# Comprimir os arquivos baixados
	if arquivos_baixados:
		arquivo_zip = os.path.join(diretorio_downloads, "anexos_ans.zip")
		comprimir_arquivos(arquivos_baixados, arquivo_zip)
		print(f"Processo concluído. Arquivos compactados em: {arquivo_zip}")
	else:
		print("Nenhum arquivo foi baixado para compactar.")

if __name__ == "__main__":
	try:
		print(f"Executando script em: {os.getcwd()}")
		print(f"Python versão: {sys.version}")
		print(f"Requests versão: {requests.__version__}")
		print(f"BeautifulSoup versão: {bs4.__version__ if 'bs4' in sys.modules else 'não disponível'}")
		main()
	except Exception as e:
		print(f"ERRO CRÍTICO: {str(e)}")
		import traceback
		traceback.print_exc()