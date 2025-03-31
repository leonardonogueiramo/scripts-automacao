import os
import re
import requests
import zipfile
import csv
import io
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

def criar_diretorio(nome_diretorio):
	"""Cria um diretório se ele não existir."""
	if not os.path.exists(nome_diretorio):
		os.makedirs(nome_diretorio)
		print(f"Diretório '{nome_diretorio}' criado com sucesso.")
	else:
		print(f"Diretório '{nome_diretorio}' já existe.")

def baixar_arquivo(url, destino, descricao=None):
	"""Baixa um arquivo da URL especificada e salva no caminho de destino."""
	try:
		resposta = requests.get(url, stream=True)
		resposta.raise_for_status()
		
		tamanho_total = int(resposta.headers.get('content-length', 0))
		progresso = tqdm(
			total=tamanho_total, 
			unit='B', 
			unit_scale=True,
			desc=descricao or os.path.basename(destino)
		)
		
		with open(destino, 'wb') as arquivo:
			for pedaco in resposta.iter_content(chunk_size=8192):
				if pedaco:
					arquivo.write(pedaco)
					progresso.update(len(pedaco))
		
		progresso.close()
		print(f"Arquivo baixado com sucesso: {destino}")
		return True
	except Exception as e:
		print(f"Erro ao baixar o arquivo {url}: {str(e)}")
		return False

def encontrar_arquivos_demonstracoes_dois_anos(url_base):
	"""Encontra os arquivos de demonstrações contábeis dos últimos 2 anos."""
	try:
		print(f"Acessando o diretório FTP: {url_base}")
		resposta = requests.get(url_base)
		resposta.raise_for_status()
		
		# Extrair links da página
		soup = BeautifulSoup(resposta.text, 'html.parser')
		links = []
		
		# Ano atual e ano anterior
		ano_atual = datetime.now().year
		anos_alvo = [str(ano_atual), str(ano_atual - 1), str(ano_atual - 2)]  # Incluímos ano atual - 2 para garantir 2 anos completos
		
		# Buscar links que contenham os anos alvo
		for link in soup.find_all('a'):
			href = link.get('href')
			if href and any(ano in href for ano in anos_alvo) and href.endswith(('.zip', '.ZIP')):
				links.append(url_base + '/' + href if not url_base.endswith('/') else url_base + href)
		
		print(f"Encontrados {len(links)} arquivos de demonstrações contábeis dos últimos 2 anos.")
		return links
	except Exception as e:
		print(f"Erro ao buscar arquivos de demonstrações: {str(e)}")
		return []

def baixar_dados_operadoras(url, destino):
	"""Baixa os dados cadastrais das operadoras ativas."""
	print(f"Baixando dados cadastrais das operadoras de {url}")
	return baixar_arquivo(url, destino, "Dados das Operadoras")

def extrair_zip(arquivo_zip, diretorio_destino):
	"""Extrai um arquivo ZIP para o diretório de destino."""
	try:
		with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
			zip_ref.extractall(diretorio_destino)
		print(f"Arquivo {arquivo_zip} extraído com sucesso para {diretorio_destino}")
		return True
	except Exception as e:
		print(f"Erro ao extrair o arquivo {arquivo_zip}: {str(e)}")
		return False

def main():
	# Diretórios para dados
	diretorio_base = "dados_ans"
	diretorio_demonstracoes = os.path.join(diretorio_base, "demonstracoes_contabeis")
	diretorio_operadoras = os.path.join(diretorio_base, "operadoras_ativas")
	
	# Criar diretórios
	criar_diretorio(diretorio_base)
	criar_diretorio(diretorio_demonstracoes)
	criar_diretorio(diretorio_operadoras)
	
	# URL base para demonstrações contábeis
	url_demonstracoes = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"
	
	# URL para dados cadastrais das operadoras
	url_operadoras = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
	
	# Baixar dados cadastrais das operadoras
	arquivo_operadoras = os.path.join(diretorio_operadoras, "operadoras_ativas.csv")
	baixar_dados_operadoras(url_operadoras, arquivo_operadoras)
	
	# Encontrar e baixar arquivos de demonstrações contábeis dos últimos 2 anos
	links_demonstracoes = encontrar_arquivos_demonstracoes_dois_anos(url_demonstracoes)
	
	if not links_demonstracoes:
		print("Não foram encontrados arquivos de demonstrações contábeis.")
		return
	
	# Baixar e extrair cada arquivo de demonstrações
	for i, url in enumerate(links_demonstracoes, 1):
		nome_arquivo = os.path.basename(url)
		caminho_arquivo = os.path.join(diretorio_demonstracoes, nome_arquivo)
		
		print(f"\nBaixando arquivo {i}/{len(links_demonstracoes)}: {nome_arquivo}")
		if baixar_arquivo(url, caminho_arquivo):
			# Extrair se for ZIP
			if nome_arquivo.lower().endswith('.zip'):
				diretorio_extracao = os.path.join(diretorio_demonstracoes, nome_arquivo.rsplit('.', 1)[0])
				criar_diretorio(diretorio_extracao)
				extrair_zip(caminho_arquivo, diretorio_extracao)
	
	print("\nDownload e extração de dados concluídos com sucesso!")
	print(f"Dados das operadoras salvos em: {arquivo_operadoras}")
	print(f"Demonstrações contábeis salvas em: {diretorio_demonstracoes}")

if __name__ == "__main__":
	main()