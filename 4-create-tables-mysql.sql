-- MySQL 8.0 Schema para Dados da ANS
-- Script para criação das tabelas

-- Criação da base de dados (caso não exista)
CREATE DATABASE IF NOT EXISTS ans_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar a base de dados criada
USE ans_database;

-- Tabela de Operadoras Ativas
-- Baseada na estrutura do arquivo Relatorio_Cadop.csv
CREATE TABLE IF NOT EXISTS operadoras (
	registro_ans VARCHAR(20) PRIMARY KEY,
	cnpj VARCHAR(20),
	razao_social VARCHAR(255),
	nome_fantasia VARCHAR(255),
	modalidade VARCHAR(100),
	logradouro VARCHAR(255),
	numero VARCHAR(20),
	complemento VARCHAR(100),
	bairro VARCHAR(100),
	cidade VARCHAR(100),
	uf CHAR(2),
	cep VARCHAR(10),
	ddd VARCHAR(5),
	telefone VARCHAR(20),
	fax VARCHAR(20),
	email VARCHAR(100),
	representante VARCHAR(255),
	cargo_representante VARCHAR(100),
	data_registro_ans DATE,
	data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
	ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Criar índices para melhorar a performance de consultas frequentes
CREATE INDEX idx_operadoras_razao_social ON operadoras(razao_social);
CREATE INDEX idx_operadoras_modalidade ON operadoras(modalidade);
CREATE INDEX idx_operadoras_uf ON operadoras(uf);

-- Tabela de Demonstrações Contábeis
-- Esta é uma estrutura base que pode precisar de ajustes conforme a estrutura exata dos arquivos
CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
	id BIGINT AUTO_INCREMENT PRIMARY KEY,
	registro_ans VARCHAR(20),
	data_base DATE,
	trimestre INT,
	ano INT,
	codigo_conta VARCHAR(50),
	descricao_conta VARCHAR(255),
	valor_conta DECIMAL(20, 2),
	
	FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);

-- Criar índices para a tabela de demonstrações
CREATE INDEX idx_demonstracoes_registro_ans ON demonstracoes_contabeis(registro_ans);
CREATE INDEX idx_demonstracoes_data_base ON demonstracoes_contabeis(data_base);
CREATE INDEX idx_demonstracoes_ano_trimestre ON demonstracoes_contabeis(ano, trimestre);

-- Tabela para monitorar os arquivos importados
CREATE TABLE IF NOT EXISTS arquivos_importados (
	id BIGINT AUTO_INCREMENT PRIMARY KEY,
	nome_arquivo VARCHAR(255) NOT NULL,
	tipo_arquivo ENUM('OPERADORA', 'DEMONSTRACAO') NOT NULL,
	data_importacao DATETIME DEFAULT CURRENT_TIMESTAMP,
	status ENUM('SUCESSO', 'ERRO', 'PARCIAL') NOT NULL,
	registros_processados INT DEFAULT 0,
	detalhes TEXT
);

-- Criar um usuário para acesso à base de dados (opcional)
-- É recomendável alterar a senha para uma mais segura
-- CREATE USER IF NOT EXISTS 'ans_user'@'localhost' IDENTIFIED BY 'senha_segura';
-- GRANT ALL PRIVILEGES ON ans_database.* TO 'ans_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Procedimento para limpar dados e reiniciar importação, se necessário
DELIMITER //
CREATE PROCEDURE limpar_dados()
BEGIN
	DELETE FROM demonstracoes_contabeis;
	DELETE FROM arquivos_importados;
	-- Não deletamos as operadoras pois são referenciadas pelas demonstrações
	-- Se quiser deletar tudo, descomente a linha abaixo
	-- DELETE FROM operadoras;
	
	SELECT 'Dados limpos com sucesso!' AS mensagem;
END //
DELIMITER ;

-- Log da criação do esquema
INSERT INTO arquivos_importados (nome_arquivo, tipo_arquivo, status, detalhes)
VALUES ('schema_creation', 'OPERADORA', 'SUCESSO', 'Criação inicial do esquema de dados');

SELECT 'Esquema de dados da ANS criado com sucesso!' AS mensagem;