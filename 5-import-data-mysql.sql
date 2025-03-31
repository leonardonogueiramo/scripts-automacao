-- MySQL 8.0 Script para importação de dados da ANS
-- Este script assume que os arquivos já foram baixados e extraídos

-- Usar a base de dados
USE ans_database;

-- Importar dados das operadoras ativas
-- Primeiro, criar uma tabela temporária para processar os dados
DROP TABLE IF EXISTS temp_operadoras;
CREATE TABLE temp_operadoras LIKE operadoras;

-- Carregar dados do CSV para a tabela temporária
-- Nota: Ajuste o caminho do arquivo conforme necessário
LOAD DATA INFILE 'D:/Documentos/TestesLeo/scripts-automacao/dados_ans/operadoras_ativas/operadoras_ativas.csv'
INTO TABLE temp_operadoras
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
	registro_ans, 
	cnpj, 
	razao_social, 
	nome_fantasia, 
	modalidade, 
	logradouro, 
	numero, 
	complemento, 
	bairro, 
	cidade, 
	uf, 
	cep, 
	ddd, 
	telefone, 
	fax, 
	email, 
	representante, 
	cargo_representante, 
	@data_registro
)
SET 
	data_registro_ans = STR_TO_DATE(@data_registro, '%d/%m/%Y'),
	data_cadastro = NOW(),
	ultima_atualizacao = NOW();

-- Verificar se houve algum erro na importação
SELECT COUNT(*) AS registros_importados FROM temp_operadoras;

-- Inserir dados na tabela principal (evitando duplicatas)
INSERT INTO operadoras
SELECT * FROM temp_operadoras
ON DUPLICATE KEY UPDATE
	cnpj = VALUES(cnpj),
	razao_social = VALUES(razao_social),
	nome_fantasia = VALUES(nome_fantasia),
	modalidade = VALUES(modalidade),
	logradouro = VALUES(logradouro),
	numero = VALUES(numero),
	complemento = VALUES(complemento),
	bairro = VALUES(bairro),
	cidade = VALUES(cidade),
	uf = VALUES(uf),
	cep = VALUES(cep),
	ddd = VALUES(ddd),
	telefone = VALUES(telefone),
	fax = VALUES(fax),
	email = VALUES(email),
	representante = VALUES(representante),
	cargo_representante = VALUES(cargo_representante),
	data_registro_ans = VALUES(data_registro_ans),
	ultima_atualizacao = NOW();

-- Registrar a importação
INSERT INTO arquivos_importados (nome_arquivo, tipo_arquivo, status, registros_processados, detalhes)
VALUES ('operadoras_ativas.csv', 'OPERADORA', 'SUCESSO', 
		(SELECT COUNT(*) FROM temp_operadoras), 
		'Importação de operadoras ativas concluída');

-- Limpar tabela temporária
DROP TABLE temp_operadoras;

-- ----------------------------------------
-- Importar demonstrações contábeis
-- ----------------------------------------

-- Procedimento para processamento de arquivos de demonstrações contábeis
-- Este procedimento deve ser executado para cada arquivo CSV de demonstrações contábeis
DROP PROCEDURE IF EXISTS importar_demonstracoes; -- Adicionado para evitar erro se já existir
DELIMITER //
CREATE PROCEDURE importar_demonstracoes(IN arquivo_path VARCHAR(255), IN ano_ref INT, IN trimestre_ref INT)
BEGIN
	DECLARE registros_total INT DEFAULT 0;
	
	-- Criar tabela temporária para os dados
	DROP TABLE IF EXISTS temp_demonstracoes;
	CREATE TABLE temp_demonstracoes (
		registro_ans VARCHAR(20),
		data_base DATE,
		codigo_conta VARCHAR(50),
		descricao_conta VARCHAR(255),
		valor_conta DECIMAL(20, 2)
	);
	
	-- Importar dados do CSV
	SET @query = CONCAT("LOAD DATA INFILE '", arquivo_path, "' 
						 INTO TABLE temp_demonstracoes 
						 FIELDS TERMINATED BY ';' 
						 ENCLOSED BY '\"' 
						 LINES TERMINATED BY '\\n' 
						 IGNORE 1 ROWS
						 (
							registro_ans, 
							@data_base, 
							codigo_conta, 
							descricao_conta, 
							@valor
						 )
						 SET 
							data_base = STR_TO_DATE(@data_base, '%d/%m/%Y'),
							valor_conta = REPLACE(REPLACE(@valor, '.', ''), ',', '.')");
	
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
	
	-- Contar registros importados
	SELECT COUNT(*) INTO registros_total FROM temp_demonstracoes;
	
	-- Inserir dados na tabela principal
	INSERT INTO demonstracoes_contabeis (registro_ans, data_base, trimestre, ano, codigo_conta, descricao_conta, valor_conta)
	SELECT 
		t.registro_ans,
		t.data_base,
		trimestre_ref,
		ano_ref,
		t.codigo_conta,
		t.descricao_conta,
		t.valor_conta
	FROM temp_demonstracoes t
	WHERE EXISTS (SELECT 1 FROM operadoras o WHERE o.registro_ans = t.registro_ans);
	
	-- Registrar a importação
	INSERT INTO arquivos_importados (nome_arquivo, tipo_arquivo, status, registros_processados, detalhes)
	VALUES (
		arquivo_path, 
		'DEMONSTRACAO', 
		'SUCESSO', 
		registros_total, 
		CONCAT('Importação de demonstrações contábeis (Ano: ', ano_ref, ', Trimestre: ', trimestre_ref, ') concluída')
	);
	
	-- Limpar tabela temporária
	DROP TABLE temp_demonstracoes;
	
	SELECT CONCAT('Importação concluída. Registros processados: ', registros_total) AS mensagem;
END //
DELIMITER ;

-- Exemplos de chamadas do procedimento (ajuste conforme os arquivos disponíveis)
CALL importar_demonstracoes('D:/Documentos/TestesLeo/scripts-automacao/dados_ans/demonstracoes_contabeis/2023/1T2023_demonstracoes.csv', 2023, 1);
-- CALL importar_demonstracoes('D:/Documentos/TestesLeo/scripts-automacao/dados_ans/demonstracoes_contabeis/2023/2T2023_demonstracoes.csv', 2023, 2);
-- CALL importar_demonstracoes('D:/Documentos/TestesLeo/scripts-automacao/dados_ans/demonstracoes_contabeis/2023/3T2023_demonstracoes.csv', 2023, 3);
-- CALL importar_demonstracoes('D:/Documentos/TestesLeo/scripts-automacao/dados_ans/demonstracoes_contabeis/2023/4T2023_demonstracoes.csv', 2023, 4);
-- CALL importar_demonstracoes('D:/Documentos/TestesLeo/scripts-automacao/dados_ans/demonstracoes_contabeis/2024/1T2024_demonstracoes.csv', 2024, 1);

-- ----------------------------------------
-- Verificar os dados importados
-- ----------------------------------------

-- Verificar arquivos importados
SELECT * FROM arquivos_importados ORDER BY data_importacao DESC;

-- Verificar quantidade de operadoras importadas
SELECT COUNT(*) AS total_operadoras FROM operadoras;

-- Verificar quantidade de demonstrações contábeis importadas por ano e trimestre
SELECT ano, trimestre, COUNT(*) AS total_registros
FROM demonstracoes_contabeis
GROUP BY ano, trimestre
ORDER BY ano DESC, trimestre DESC;

-- Verificar demonstrações contábeis por modalidade de operadora
SELECT 
	o.modalidade,
	dc.ano,
	dc.trimestre,
	COUNT(*) AS total_registros
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras o ON dc.registro_ans = o.registro_ans
GROUP BY 
	o.modalidade, dc.ano, dc.trimestre
ORDER BY 
	dc.ano DESC, dc.trimestre DESC, o.modalidade;

-- Verificar se existem operadoras sem demonstrações contábeis
SELECT 
	o.registro_ans,
	o.razao_social,
	o.modalidade
FROM 
	operadoras o
WHERE 
	NOT EXISTS (SELECT 1 FROM demonstracoes_contabeis dc WHERE dc.registro_ans = o.registro_ans)
ORDER BY
	o.modalidade, o.razao_social;