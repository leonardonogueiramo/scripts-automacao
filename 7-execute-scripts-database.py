import mysql.connector

def executar_script_sql(host, usuario, senha, database, arquivo_sql):
	"""
	Conecta ao banco de dados MySQL e executa um script SQL.

	Args:
		host (str): Endereço do servidor MySQL.
		usuario (str): Nome de usuário para conectar ao MySQL.
		senha (str): Senha para conectar ao MySQL.
		database (str): Nome do banco de dados a ser usado.
		arquivo_sql (str): Caminho para o arquivo SQL a ser executado.
	"""
	conexao = None  # Inicializar conexao fora do bloco try
	try:
		# Tentar conectar ao MySQL sem especificar o banco de dados para criar
		conexao = mysql.connector.connect(
			host=host,
			user=usuario,
			password=senha
		)
		cursor = conexao.cursor()

		# Criar o banco de dados se ele não existir
		try:
			cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
			print(f"Banco de dados '{database}' criado ou já existente.")
		except mysql.connector.Error as create_db_error:
			print(f"Erro ao criar o banco de dados: {create_db_error}")
			return  # Abortar a execução da função se a criação do banco falhar

		# Conectar ao banco de dados específico
		conexao.database = database

		# Abrir e ler o arquivo SQL
		with open(arquivo_sql, 'r', encoding='utf-8') as arquivo:
			sql_script = arquivo.read()

		# Executar o script SQL
		for comando in sql_script.split(';'):  # Dividir o script em comandos individuais
			comando = comando.strip()  # Remover espaços em branco extras
			if comando:  # Evitar executar comandos vazios
				try:
					cursor.execute(comando)
					if comando.upper().startswith("SELECT"):
						# Imprimir resultados para comandos SELECT
						resultados = cursor.fetchall()
						colunas = [desc[0] for desc in cursor.description]
						print("\nResultados:")
						print(colunas)  # Imprimir nomes das colunas
						for linha in resultados:
							print(linha)
					elif comando.upper().startswith("CREATE PROCEDURE") or comando.upper().startswith("DROP PROCEDURE"):
						# Lidar com DELIMITER
						continue  # Ignorar comandos de procedimento
					else:
						conexao.commit()  # Commit para outras operações (INSERT, UPDATE, DELETE)
						print("Comando executado com sucesso.")
				except Exception as e:
					print(f"Erro ao executar o comando: {comando}\nErro: {e}")
					if conexao:  # Verificar se a conexão foi estabelecida antes do rollback
						conexao.rollback()

		print(f"Script SQL '{arquivo_sql}' executado com sucesso.")

	except mysql.connector.Error as erro:
		print(f"Erro ao conectar ao MySQL: {erro}")

	except FileNotFoundError:
		print(f"Erro: Arquivo SQL '{arquivo_sql}' não encontrado.")

	except Exception as e:
		print(f"Erro inesperado: {e}")

	finally:
		# Fechar o cursor e a conexão
		if conexao:  # Verificar se a conexão foi estabelecida antes de tentar fechar
			if conexao.is_connected():
				cursor.close()
				conexao.close()
				print("Conexão ao MySQL fechada.")

if __name__ == "__main__":
	# Configurações do banco de dados
	host = "localhost"
	usuario = "root"
	senha = "938612ot"  # Substitua pela sua senha real
	database = "ans_database"

	# Arquivos SQL a serem executados
	arquivos_sql = [
		"4-create-tables-mysql.sql",
		"5-import-data-mysql.sql",
		"6-analytical-queries.sql"
	]

	# Executar os scripts SQL
	for arquivo_sql in arquivos_sql:
		print(f"\nExecutando script: {arquivo_sql}")
		executar_script_sql(host, usuario, senha, database, arquivo_sql)

	print("\nTodos os scripts SQL foram executados.")