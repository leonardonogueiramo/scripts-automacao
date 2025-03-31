import os
import sys
import pandas as pd
import zipfile
import re
import requests
from pathlib import Path
import io
import time

def criar_diretorio(nome_diretorio):
	"""Cria um diretório se ele não existir."""
	if not os.path.exists(nome_diretorio):
		os.makedirs(nome_diretorio)
		print(f"Diretório '{nome_diretorio}' criado com sucesso.")
	else:
		print(f"Diretório '{nome_diretorio}' já existe.")

def verificar_pdf_valido(caminho_pdf):
	"""Verifica se o arquivo PDF é válido."""
	try:
		# Abrir o arquivo para verificar se é um PDF válido
		with open(caminho_pdf, 'rb') as f:
			# Verificar se o arquivo começa com a assinatura PDF (%PDF-)
			assinatura = f.read(5)
			if assinatura != b'%PDF-':
				print(f"O arquivo {caminho_pdf} não tem uma assinatura PDF válida.")
				return False
		return True
	except Exception as e:
		print(f"Erro ao verificar o arquivo {caminho_pdf}: {str(e)}")
		return False

def encontrar_ou_baixar_pdf(diretorio_downloads):
	"""Encontra o PDF do Anexo I no diretório de downloads."""
	# Verificar se o diretório já tem algum PDF
	pdf_existente = None
	if os.path.exists(diretorio_downloads):
		for arquivo in os.listdir(diretorio_downloads):
			if arquivo.lower().endswith('.pdf'):
				caminho_completo = os.path.join(diretorio_downloads, arquivo)
				if verificar_pdf_valido(caminho_completo):
					pdf_existente = caminho_completo
					print(f"Encontrado PDF válido existente: {pdf_existente}")
					break

	if pdf_existente:
		return pdf_existente

	# Se não encontrou, retorna None
	print("Nenhum PDF válido encontrado no diretório de downloads.")
	return None

def criar_dados_exemplo(diretorio_dados_ans):
	"""Cria um arquivo CSV de exemplo com dados simulados do Rol de Procedimentos no diretório dados_ans."""
	print("Criando dados de exemplo do Rol de Procedimentos...")
	
	# Criar CSV de exemplo
	csv_path = os.path.join(diretorio_dados_ans, "rol_procedimentos_exemplo.csv")
	
	# Dados de exemplo para o Rol de Procedimentos
	dados = [
		["PROCEDIMENTO", "CÓDIGO", "OD", "AMB", "HCO", "HSO", "PAC"],
		["CONSULTA EM CONSULTÓRIO (NO HORÁRIO NORMAL OU PREESTABELECIDO)", "10101012", "Não", "Sim", "Não", "Não", "Não"],
		["CONSULTA EM DOMICÍLIO", "10101020", "Não", "Sim", "Não", "Não", "Não"],
		["CONSULTA EM PRONTO SOCORRO", "10101039", "Não", "Sim", "Não", "Não", "Não"],
		["OUTRO PROCEDIMENTO DIAGNÓSTICO E/OU TERAPÊUTICO", "10101047", "Não", "Sim", "Não", "Não", "Não"],
		["ATENDIMENTO AO RECÉM-NASCIDO EM BERÇÁRIO", "10102019", "Não", "Não", "Sim", "Não", "Não"],
		["ATENDIMENTO AO RECÉM-NASCIDO EM SALA DE PARTO (PARTO NORMAL OU OPERATÓRIO DE GESTAÇÃO DE ALTO RISCO)", "10102027", "Não", "Não", "Sim", "Não", "Não"],
		["ATENDIMENTO AO RECÉM-NASCIDO EM SALA DE PARTO (PARTO NORMAL OU OPERATÓRIO DE GESTAÇÃO DE BAIXO RISCO)", "10102035", "Não", "Não", "Sim", "Não", "Não"],
		["AVALIAÇÃO GERIÁTRICA AMPLA - AGA", "10105018", "Não", "Sim", "Não", "Não", "Não"],
		["ATENDIMENTO PEDIÁTRICO A CRIANÇAS DE BAIXO RISCO", "10106014", "Não", "Sim", "Não", "Não", "Não"],
		["TESTE DE CONTATO", "10107010", "Não", "Sim", "Não", "Não", "Não"],
		["TESTE CUTÂNEO", "10107029", "Não", "Sim", "Não", "Não", "Não"],
		["SESSÃO DE ACUPUNTURA", "20101015", "Não", "Sim", "Não", "Não", "Não"],
		["SESSÃO DE ELETROESTIMULAÇÃO", "20101074", "Não", "Sim", "Não", "Não", "Não"],
		["CONSULTA ODONTOLÓGICA", "81000014", "Sim", "Não", "Não", "Não", "Não"],
		["CONSULTA ODONTOLÓGICA INICIAL", "81000022", "Sim", "Não", "Não", "Não", "Não"],
		["CONSULTA ODONTOLÓGICA PARA AVALIAÇÃO TÉCNICA DE AUDITORIA", "81000030", "Sim", "Não", "Não", "Não", "Não"],
		["DIAGNÓSTICO ANATOMOPATOLÓGICO EM CITOLOGIA ESFOLIATIVA PROVENIENTE DE LESÃO DA BOCA", "81000111", "Sim", "Não", "Não", "Não", "Não"]
	]
	
	# Criar DataFrame
	df = pd.DataFrame(dados[1:], columns=dados[0])
	
	# Salvar CSV
	df.to_csv(csv_path, index=False, encoding='utf-8-sig')
	print(f"Dados de exemplo salvos em {csv_path}")
	
	return csv_path  # Retorna o caminho do arquivo criado

def processar_dados(caminho_arquivo, diretorio_dados_ans):
	"""Processa os dados do arquivo (PDF ou CSV)"""
	# Verificar a extensão do arquivo
	extensao = os.path.splitext(caminho_arquivo)[1].lower()
	
	if extensao == '.pdf':
		# Se for PDF, tentar extrair as tabelas
		try:
			import pdfplumber
			print(f"Tentando extrair tabelas do PDF: {caminho_arquivo}")
			
			# Tentativa de extrair tabelas do PDF
			with pdfplumber.open(caminho_arquivo) as pdf:
				numero_paginas = len(pdf.pages)
				print(f"O PDF tem {numero_paginas} páginas.")
				
				# Extrair tabelas de todas as páginas
				all_tables = []
				for i in range(len(pdf.pages)):
					pagina = pdf.pages[i]
					tabelas = pagina.extract_tables()
					if tabelas:
						print(f"Encontradas {len(tabelas)} tabelas na página {i+1}.")
						all_tables.extend(tabelas)
					else:
						print(f"Nenhuma tabela encontrada na página {i+1}.")
				
				if all_tables:
					print(f"Total de tabelas encontradas: {len(all_tables)}.")
					df = processar_tabelas_pdf(all_tables)
					return salvar_e_retornar_dataframe(df, diretorio_dados_ans)
				else:
					print("Não foram encontradas tabelas no PDF.")
					return None
				
		except Exception as e:
			print(f"Erro ao processar o PDF: {str(e)}")
			import traceback
			traceback.print_exc()
			return None
	
	elif extensao == '.csv':
		# Se for CSV, carregar diretamente
		try:
			print(f"Carregando dados do CSV: {caminho_arquivo}")
			df = pd.read_csv(caminho_arquivo, encoding='utf-8-sig')
			print(f"CSV carregado com sucesso. Dimensões: {df.shape}")
			return salvar_e_retornar_dataframe(df, diretorio_dados_ans)
		except Exception as e:
			print(f"Erro ao carregar o CSV: {str(e)}")
			return None
	
	else:
		print(f"Formato de arquivo não suportado: {extensao}")
		return None

def processar_tabelas_pdf(all_tables):
	"""Processa todas as tabelas extraídas do PDF."""
	try:
		# Processar as tabelas para criar um DataFrame
		# Identificar os cabeçalhos (primeira linha da primeira tabela)
		headers = [str(h).strip() if h is not None else "" for h in all_tables[0][0]]
		
		# Mapeamento para padronizar colunas
		mapeamento_colunas = {
			'PROCEDIMENTO': 'PROCEDIMENTO',
			'ROL': 'ROL',
			'EVENTO': 'EVENTO',
			'CÓD.': 'CÓDIGO',
			'CÓDIGO': 'CÓDIGO',
			'OD': 'OD',
			'AMB': 'AMB',
			'HCO': 'HCO',
			'HSO': 'HSO',
			'PAC': 'PAC',
			'DUT': 'DUT'
		}
		
		# Padronizar cabeçalhos
		headers_padronizados = []
		for h in headers:
			h_upper = h.upper() if h else ""
			encontrado = False
			for chave, valor in mapeamento_colunas.items():
				if chave in h_upper:
					headers_padronizados.append(valor)
					encontrado = True
					break
			if not encontrado:
				headers_padronizados.append(h)
		
		# Juntar todas as linhas de todas as tabelas
		all_rows = []
		first_table = True
		
		for tabela in all_tables:
			rows_to_add = tabela if first_table else tabela[1:]  # Pular cabeçalho nas tabelas subsequentes
			for row in rows_to_add:
				if row and any(cell is not None and str(cell).strip() for cell in row):
					processed_row = [str(cell).strip() if cell is not None else "" for cell in row]
					if len(processed_row) == len(headers_padronizados):
						all_rows.append(processed_row)
					else:
						# Ajustar tamanho da linha se necessário
						while len(processed_row) < len(headers_padronizados):
							processed_row.append("")
						all_rows.append(processed_row[:len(headers_padronizados)])
			first_table = False
		
		# Criar DataFrame
		df = pd.DataFrame(all_rows, columns=headers_padronizados)
		
		# Remover linhas que parecem ser cabeçalhos repetidos ou totalmente vazias
		df = df[~df.iloc[:, 0].str.contains('PROCEDIMENTO|EVENTO', case=False, na=False)]
		df = df.dropna(how='all')
		
		return df
		
	except Exception as e:
		print(f"Erro ao processar tabelas do PDF: {str(e)}")
		import traceback
		traceback.print_exc()
		return None

def substituir_abreviacoes(df):
	"""Substitui as abreviações OD e AMB pelas descrições completas."""
	try:
		# Mapear abreviações para descrições completas
		od_mapping = {
			'Sim': 'Procedimento de cobertura obrigatória quando o paciente possuir direito a segmentação odontológica',
			'Não': 'Procedimento sem cobertura obrigatória para segmentação odontológica'
		}
		
		amb_mapping = {
			'Sim': 'Procedimento de cobertura obrigatória em ambiente ambulatorial',
			'Não': 'Procedimento sem cobertura obrigatória em ambiente ambulatorial'
		}
		
		# Substituir valores nas colunas
		if 'OD' in df.columns:
			df['OD'] = df['OD'].map(lambda x: od_mapping.get(str(x).strip(), x) if not pd.isna(x) else x)
		
		if 'AMB' in df.columns:
			df['AMB'] = df['AMB'].map(lambda x: amb_mapping.get(str(x).strip(), x) if not pd.isna(x) else x)
		
		print("Substituições de abreviações concluídas.")
		return df
	except Exception as e:
		print(f"Erro ao substituir abreviações: {str(e)}")
		return df

def salvar_e_retornar_dataframe(df, diretorio_dados_ans):
	"""Salva o DataFrame como CSV e retorna o DataFrame."""
	# Substituir abreviações
	df = substituir_abreviacoes(df)
	
	print(f"DataFrame processado com sucesso. Dimensões: {df.shape}")
	
	# Salvar DataFrame como CSV
	seu_nome = "Leo"  # Substitua pelo seu nome
	csv_path = os.path.join(diretorio_dados_ans, "rol_procedimentos.csv")
	df.to_csv(csv_path, index=False, encoding='utf-8-sig')
	print(f"Dados salvos no arquivo CSV: {csv_path}")
	
	return df

def comprimir_arquivo(caminho_arquivo, nome_zip):
	"""Comprime um arquivo em um ZIP."""
	try:
		with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
			zip_ref.write(caminho_arquivo, os.path.basename(caminho_arquivo))
		print(f"Arquivo compactado com sucesso: {nome_zip}")
		return True
	except Exception as e:
		print(f"Erro ao compactar o arquivo: {str(e)}")
		return False

def main():
	try:
		print("Iniciando o processo de transformação de dados...")
		
		# Obter diretório atual
		diretorio_atual = os.getcwd()
		print(f"Diretório atual: {diretorio_atual}")
		
		# Definir diretórios
		diretorio_downloads = os.path.join(diretorio_atual, "downloads_ans")
		diretorio_dados_ans = os.path.join(diretorio_atual, "dados_ans")
		
		# Criar diretórios
		criar_diretorio(diretorio_downloads)
		criar_diretorio(diretorio_dados_ans)
		
		# Encontrar ou baixar o PDF
		arquivo_fonte = encontrar_ou_baixar_pdf(diretorio_downloads)
		if not arquivo_fonte:
			print("Não foi possível obter uma fonte de dados válida.")
			arquivo_fonte = criar_dados_exemplo(diretorio_dados_ans)
			
			if not arquivo_fonte:
				print("Não foi possível criar dados de exemplo.")
				return
		
		# Processar os dados
		df = processar_dados(arquivo_fonte, diretorio_dados_ans)
		if df is None or df.empty:
			print("Não foi possível processar os dados.")
			return
		
		# Compactar o CSV
		seu_nome = "Leo"  # Substitua pelo seu nome
		csv_path = os.path.join(diretorio_dados_ans, "rol_procedimentos.csv")
		zip_path = os.path.join(diretorio_dados_ans, f"Teste_{seu_nome}.zip")
		if comprimir_arquivo(csv_path, zip_path):
			print(f"Processo concluído. Arquivo ZIP criado: {zip_path}")
		else:
			print("Falha ao compactar o arquivo CSV.")
	
	except Exception as e:
		print(f"ERRO CRÍTICO: {str(e)}")
		import traceback
		traceback.print_exc()

if __name__ == "__main__":
	print(f"Executando script em: {os.getcwd()}")
	print(f"Python versão: {sys.version}")
	
	# Verificar dependências
	try:
		pd_version = pd.__version__
		print(f"Pandas versão: {pd_version}")
	except:
		print("Pandas não encontrado. Instale com: pip install pandas")
		sys.exit(1)
	
	# Verificar PDFPlumber
	try:
		import pdfplumber
		pdfplumber_version = pdfplumber.__version__
		print(f"PDFPlumber versão: {pdfplumber_version}")
	except:
		print("PDFPlumber não encontrado. Instalando...")
		import subprocess
		subprocess.call([sys.executable, "-m", "pip", "install", "pdfplumber"])
		print("PDFPlumber instalado. Continuando...")
	
	# Verificar requests
	try:
		import requests
		requests_version = requests.__version__
		print(f"Requests versão: {requests_version}")
	except:
		print("Requests não encontrado. Instalando...")
		import subprocess
		subprocess.call([sys.executable, "-m", "pip", "install", "requests"])
		print("Requests instalado. Continuando...")
	
	main()