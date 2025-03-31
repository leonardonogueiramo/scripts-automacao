from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Variável global para armazenar os dados das operadoras
df_operadoras = None

def criar_dados_exemplo():
	"""Cria dados de exemplo para teste quando não há arquivo CSV disponível"""
	print("Criando dados de exemplo para teste...")
	
	# Dados de exemplo
	operadoras = [
		{
			"registro_ans": "335100",
			"cnpj": "29309127000179",
			"razao_social": "AMIL ASSISTÊNCIA MÉDICA INTERNACIONAL S.A.",
			"nome_fantasia": "AMIL",
			"modalidade": "Medicina de Grupo",
			"logradouro": "RUA ARQUITETO OLAVO REDIG DE CAMPOS",
			"numero": "105",
			"complemento": "TORRE B - 6º ao 21º ANDAR",
			"bairro": "BROOKLIN NOVO",
			"cidade": "SÃO PAULO",
			"uf": "SP",
			"cep": "04711904",
			"ddd": "11",
			"telefone": "31878000",
			"fax": "31878000",
			"email": "regulamentacao@amil.com.br",
			"representante": "ROBERTO MALTMAN",
			"cargo_representante": "Diretor",
			"data_registro": "01/12/1998"
		},
		{
			"registro_ans": "304701",
			"cnpj": "83189525000182",
			"razao_social": "UNIMED JOINVILLE COOPERATIVA DE TRABALHO MÉDICO",
			"nome_fantasia": "UNIMED JOINVILLE",
			"modalidade": "Cooperativa Médica",
			"logradouro": "RUA OTTO BOEHM",
			"numero": "478",
			"complemento": "",
			"bairro": "CENTRO",
			"cidade": "JOINVILLE",
			"uf": "SC",
			"cep": "89201700",
			"ddd": "47",
			"telefone": "34419100",
			"fax": "34419100",
			"email": "diretoria@unimedjoinville.com.br",
			"representante": "JOSE CARLOS GOMES FERREIRA",
			"cargo_representante": "Diretor Presidente",
			"data_registro": "06/10/1998"
		},
		{
			"registro_ans": "326305",
			"cnpj": "61486565000112",
			"razao_social": "BRADESCO SAÚDE S.A.",
			"nome_fantasia": "BRADESCO SAÚDE",
			"modalidade": "Seguradora Especializada em Saúde",
			"logradouro": "RUA BARÃO DE ITAPAGIPE",
			"numero": "225",
			"complemento": "",
			"bairro": "RIO COMPRIDO",
			"cidade": "RIO DE JANEIRO",
			"uf": "RJ",
			"cep": "20261901",
			"ddd": "21",
			"telefone": "25034581",
			"fax": "25034581",
			"email": "4673.diretoria@bradesco.com.br",
			"representante": "FLAVIO BITTER",
			"cargo_representante": "Diretor",
			"data_registro": "08/04/1999"
		},
		{
			"registro_ans": "302147",
			"cnpj": "02904065000137",
			"razao_social": "HAPVIDA ASSISTÊNCIA MÉDICA LTDA",
			"nome_fantasia": "HAPVIDA ASSISTÊNCIA MÉDICA",
			"modalidade": "Medicina de Grupo",
			"logradouro": "AVENIDA HERÁCLITO GRAÇA",
			"numero": "406",
			"complemento": "",
			"bairro": "CENTRO",
			"cidade": "FORTALEZA",
			"uf": "CE",
			"cep": "60140060",
			"ddd": "85",
			"telefone": "40083033",
			"fax": "40083033",
			"email": "juridico@hapvida.com.br",
			"representante": "JORGE FONTOURA PINHEIRO KOREN DE LIMA",
			"cargo_representante": "Diretor",
			"data_registro": "06/10/1998"
		},
		{
			"registro_ans": "343889",
			"cnpj": "02663552000108",
			"razao_social": "UNIMED-RIO COOPERATIVA DE TRABALHO MEDICO DO RIO DE JANEIRO",
			"nome_fantasia": "UNIMED-RIO",
			"modalidade": "Cooperativa Médica",
			"logradouro": "AVENIDA ARMANDO LOMBARDI",
			"numero": "400",
			"complemento": "LOJAS 101 A 105/501 A 514",
			"bairro": "BARRA DA TIJUCA",
			"cidade": "RIO DE JANEIRO",
			"uf": "RJ",
			"cep": "22640000",
			"ddd": "21",
			"telefone": "45474969",
			"fax": "45474969",
			"email": "presidencia@unimedrio.com.br",
			"representante": "ANTONIO ROMEU SCOFANO JUNIOR",
			"cargo_representante": "Diretor Presidente",
			"data_registro": "18/05/2001"
		},
		{
			"registro_ans": "307301",
			"cnpj": "54484753000149",
			"razao_social": "SULAMÉRICA COMPANHIA DE SEGURO SAÚDE",
			"nome_fantasia": "SULAMÉRICA SAÚDE",
			"modalidade": "Seguradora Especializada em Saúde",
			"logradouro": "RUA BEATRIZ LARRAGOITI LUCAS",
			"numero": "121",
			"complemento": "ANDAR 01",
			"bairro": "CIDADE NOVA",
			"cidade": "RIO DE JANEIRO",
			"uf": "RJ",
			"cep": "20211903",
			"ddd": "21",
			"telefone": "38125000",
			"fax": "38125000",
			"email": "presidencia@sulamerica.com.br",
			"representante": "GABRIEL PORTELLA FAGUNDES FILHO",
			"cargo_representante": "Diretor",
			"data_registro": "30/12/1998"
		},
		{
			"registro_ans": "417807",
			"cnpj": "00333833000130",
			"razao_social": "AMERON - ASSISTÊNCIA MÉDICA RONDÔNIA LTDA",
			"nome_fantasia": "AMERON",
			"modalidade": "Medicina de Grupo",
			"logradouro": "AV. CALAMA",
			"numero": "2615",
			"complemento": "",
			"bairro": "LIBERDADE",
			"cidade": "PORTO VELHO",
			"uf": "RO",
			"cep": "76803884",
			"ddd": "69",
			"telefone": "21812000",
			"fax": "21812000",
			"email": "diretoria@ameronsaude.com.br",
			"representante": "MANOEL CARLOS CARREIRO JUNIOR",
			"cargo_representante": "Diretor",
			"data_registro": "16/11/2004"
		},
		{
			"registro_ans": "313751",
			"cnpj": "54484753000149",
			"razao_social": "OPERADORA NACIONAL DE PLANOS DE SAÚDE EXEMPLO",
			"nome_fantasia": "ONPS SAÚDE",
			"modalidade": "Medicina de Grupo",
			"logradouro": "AVENIDA PAULISTA",
			"numero": "1000",
			"complemento": "ANDAR 10",
			"bairro": "BELA VISTA",
			"cidade": "SÃO PAULO",
			"uf": "SP",
			"cep": "01310100",
			"ddd": "11",
			"telefone": "31234567",
			"fax": "31234567",
			"email": "contato@onpssaude.com.br",
			"representante": "MARIA SILVA",
			"cargo_representante": "Diretora",
			"data_registro": "05/03/2000"
		}
	]
	
	return pd.DataFrame(operadoras)

def carregar_dados():
	"""Carrega os dados das operadoras do CSV ou cria dados de exemplo se não houver arquivo"""
	global df_operadoras
	try:
		# Caminho para o arquivo CSV das operadoras ativas
		arquivo_csv = 'dados_ans/operadoras_ativas/operadoras_ativas.csv'
		
		# Verificar se o arquivo existe
		if os.path.exists(arquivo_csv):
			# Tentar diferentes encodings
			for encoding in ['utf-8', 'latin1', 'ISO-8859-1']:
				try:
					print(f"Tentando carregar o CSV com encoding {encoding}...")
					df_operadoras = pd.read_csv(arquivo_csv, sep=';', encoding=encoding)
					break
				except UnicodeDecodeError:
					continue
				except Exception as e:
					print(f"Erro ao carregar com encoding {encoding}: {str(e)}")
					continue
			
			if df_operadoras is None:
				print("Não foi possível carregar o CSV com nenhum encoding. Criando dados de exemplo.")
				df_operadoras = criar_dados_exemplo()
		else:
			print(f"Arquivo {arquivo_csv} não encontrado. Criando dados de exemplo.")
			df_operadoras = criar_dados_exemplo()
		
		# Renomear colunas para padronizar, baseado na estrutura real do CSV
		# Só renomeia se as colunas existirem no DataFrame
		colunas_renomeadas = {
			'Registro ANS': 'registro_ans',
			'CNPJ': 'cnpj',
			'Razão Social': 'razao_social',
			'Nome Fantasia': 'nome_fantasia',
			'Modalidade': 'modalidade',
			'Logradouro': 'logradouro',
			'Número': 'numero',
			'Complemento': 'complemento',
			'Bairro': 'bairro',
			'Cidade': 'cidade',
			'UF': 'uf',
			'CEP': 'cep',
			'DDD': 'ddd',
			'Telefone': 'telefone',
			'Fax': 'fax',
			'Endereço eletrônico': 'email',
			'Representante': 'representante',
			'Cargo Representante': 'cargo_representante',
			'Data Registro ANS': 'data_registro'
		}
		
		# Verificar quais colunas existem e renomeá-las
		colunas_existentes = {col: novo_nome for col, novo_nome in colunas_renomeadas.items() 
							  if col in df_operadoras.columns}
		if colunas_existentes:
			df_operadoras = df_operadoras.rename(columns=colunas_existentes)
		
		print(f"Dados carregados com sucesso. {len(df_operadoras)} operadoras encontradas.")
		
		# Garantir que todas as colunas necessárias existam
		for col in ['registro_ans', 'cnpj', 'razao_social', 'nome_fantasia', 'modalidade', 
				   'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 
				   'cep', 'ddd', 'telefone', 'email']:
			if col not in df_operadoras.columns:
				df_operadoras[col] = ""
		
		return True
	except Exception as e:
		print(f"Erro ao carregar dados: {str(e)}")
		# Em caso de erro, usar dados de exemplo
		print("Usando dados de exemplo como fallback.")
		df_operadoras = criar_dados_exemplo()
		return True

@app.route('/api/operadoras/busca', methods=['GET'])
def buscar_operadoras():
	"""
	Rota para buscar operadoras por termo textual
	Parâmetros:
		termo: Termo de busca (obrigatório)
		limite: Limite de resultados (opcional, padrão 10)
	"""
	# Verificar se os dados foram carregados
	global df_operadoras
	if df_operadoras is None:
		sucesso = carregar_dados()
		if not sucesso:
			return jsonify({
				'erro': 'Não foi possível carregar os dados das operadoras'
			}), 500
	
	# Obter parâmetros da requisição
	termo_busca = request.args.get('termo', '')
	limite = request.args.get('limite', 10, type=int)
	
	# Validar parâmetros
	if not termo_busca:
		return jsonify({
			'erro': 'O parâmetro "termo" é obrigatório'
		}), 400
	
	# Realizar a busca
	try:
		# Converter o termo de busca para lowercase para comparação case-insensitive
		termo_lower = termo_busca.lower()
		
		# Função para pontuar a relevância de uma correspondência
		def pontuacao_relevancia(row):
			pontos = 0
			
			# Verificar correspondências em diferentes campos
			campos_busca = ['razao_social', 'nome_fantasia', 'registro_ans', 'cnpj']
			for campo in campos_busca:
				if campo in row and pd.notna(row[campo]):
					valor = str(row[campo]).lower()
					
					# Correspondência exata (maior pontuação)
					if valor == termo_lower:
						pontos += 10
					# Início da string (alta pontuação)
					elif valor.startswith(termo_lower):
						pontos += 8
					# Contém como palavra completa
					elif re.search(r'\b' + re.escape(termo_lower) + r'\b', valor):
						pontos += 5
					# Contém em qualquer lugar
					elif termo_lower in valor:
						pontos += 3
			
			return pontos
		
		# Aplicar a função de pontuação a cada linha
		df_operadoras['relevancia'] = df_operadoras.apply(pontuacao_relevancia, axis=1)
		
		# Filtrar linhas com pontuação > 0 e ordenar por relevância
		resultados_df = df_operadoras[df_operadoras['relevancia'] > 0].sort_values(
			by='relevancia', ascending=False
		).head(limite)
		
		# Converter para lista de dicionários para o JSON
		resultados = resultados_df.to_dict(orient='records')
		
		# Limpar a coluna de relevância do DataFrame original
		if 'relevancia' in df_operadoras.columns:
			df_operadoras = df_operadoras.drop('relevancia', axis=1)
		
		return jsonify({
			'total': len(resultados),
			'termo_busca': termo_busca,
			'resultados': resultados
		})
	
	except Exception as e:
		print(f"Erro na busca: {str(e)}")
		return jsonify({
			'erro': f'Erro ao processar a busca: {str(e)}'
		}), 500

@app.route('/api/operadoras/detalhes/<registro_ans>', methods=['GET'])
def detalhes_operadora(registro_ans):
	"""Rota para obter detalhes de uma operadora específica pelo registro ANS"""
	# Verificar se os dados foram carregados
	global df_operadoras
	if df_operadoras is None:
		sucesso = carregar_dados()
		if not sucesso:
			return jsonify({
				'erro': 'Não foi possível carregar os dados das operadoras'
			}), 500
	
	try:
		# Filtrar pelo registro ANS
		operadora = df_operadoras[df_operadoras['registro_ans'] == registro_ans]
		
		if operadora.empty:
			return jsonify({
				'erro': f'Operadora com registro {registro_ans} não encontrada'
			}), 404
		
		# Retornar os detalhes da operadora
		return jsonify(operadora.iloc[0].to_dict())
	
	except Exception as e:
		print(f"Erro ao buscar detalhes: {str(e)}")
		return jsonify({
			'erro': f'Erro ao buscar detalhes da operadora: {str(e)}'
		}), 500

@app.route('/api/operadoras/modalidades', methods=['GET'])
def listar_modalidades():
	"""Rota para listar as modalidades disponíveis e quantidade de operadoras por modalidade"""
	# Verificar se os dados foram carregados
	global df_operadoras
	if df_operadoras is None:
		sucesso = carregar_dados()
		if not sucesso:
			return jsonify({
				'erro': 'Não foi possível carregar os dados das operadoras'
			}), 500
	
	try:
		# Contar operadoras por modalidade
		contagem = df_operadoras['modalidade'].value_counts().to_dict()
		
		# Formatar resultado
		modalidades = [
			{'nome': modalidade, 'quantidade': quantidade}
			for modalidade, quantidade in contagem.items()
		]
		
		return jsonify({
			'total': len(modalidades),
			'modalidades': modalidades
		})
	
	except Exception as e:
		print(f"Erro ao listar modalidades: {str(e)}")
		return jsonify({
			'erro': f'Erro ao listar modalidades: {str(e)}'
		}), 500

@app.route('/api/status', methods=['GET'])
def status():
	"""Rota para verificar o status da API"""
	global df_operadoras
	
	# Se os dados ainda não foram carregados, tenta carregar
	if df_operadoras is None:
		carregar_dados()
	
	return jsonify({
		'status': 'online',
		'versao': '1.0.0',
		'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'dados_carregados': df_operadoras is not None,
		'total_operadoras': len(df_operadoras) if df_operadoras is not None else 0
	})

if __name__ == '__main__':
	# Carregar dados ao iniciar a aplicação
	carregar_dados()
	
	# Iniciar servidor Flask
	porta = int(os.environ.get("PORT", 5000))
	print(f"Iniciando servidor API na porta {porta}...")
	app.run(host='0.0.0.0', port=porta, debug=True)