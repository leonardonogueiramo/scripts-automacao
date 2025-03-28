-- MySQL 8.0 Consultas Analíticas para Dados da ANS
-- Este script responde às perguntas analíticas do teste

-- Usar a base de dados
USE ans_database;

-- ----------------------------------------
-- PARTE 1: Verificação dos dados importados
-- ----------------------------------------

-- Verificar tabelas disponíveis
SHOW TABLES;

-- Verificar estrutura da tabela de operadoras
DESCRIBE operadoras;

-- Verificar estrutura da tabela de demonstrações contábeis
DESCRIBE demonstracoes_contabeis;

-- Verificar quantidade de operadoras importadas
SELECT COUNT(*) AS total_operadoras FROM operadoras;

-- Verificar quantidade de demonstrações contábeis importadas por ano e trimestre
SELECT 
	ano, 
	trimestre, 
	COUNT(*) AS total_registros
FROM 
	demonstracoes_contabeis
GROUP BY 
	ano, trimestre
ORDER BY 
	ano DESC, trimestre DESC;

-- ----------------------------------------
-- Questão 1: Quais as 10 operadoras com maiores despesas em "EVENTOS/ SINISTROS
-- CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR" no último trimestre?
-- ----------------------------------------

-- Primeiro, identificar o último trimestre disponível na base de dados
WITH ultimo_trimestre AS (
	SELECT 
		ano, 
		trimestre
	FROM (
		SELECT 
			ano, 
			trimestre,
			ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
		FROM 
			demonstracoes_contabeis
		GROUP BY 
			ano, trimestre
	) t
	WHERE ordem = 1
)

-- Agora, buscar as 10 operadoras com maiores despesas no último trimestre
SELECT 
	op.registro_ans,
	op.razao_social,
	op.modalidade,
	ABS(dc.valor_conta) AS valor_despesa, -- Usamos ABS para tratar valores negativos como positivos
	CONCAT(dc.ano, ' - ', dc.trimestre, 'º trimestre') AS periodo,
	dc.codigo_conta,
	dc.descricao_conta
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimo_trimestre ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
WHERE 
	-- Vamos considerar as contas de eventos/sinistros médico-hospitalares
	-- Os códigos e descrições podem variar conforme a estrutura real dos dados
	(
		dc.codigo_conta = '411111' 
		OR dc.codigo_conta LIKE '4111%'
		OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
		OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
	)
ORDER BY 
	valor_despesa DESC
LIMIT 10;

-- ----------------------------------------
-- Questão 2: Quais as 10 operadoras com maiores despesas nessa categoria no último ano?
-- ----------------------------------------

-- Método 1: Último ano completo (4 trimestres)
-- Primeiro, determinar qual é o último ano com 4 trimestres completos
WITH anos_completos AS (
	SELECT 
		ano,
		COUNT(DISTINCT trimestre) AS qtd_trimestres
	FROM 
		demonstracoes_contabeis
	GROUP BY 
		ano
	HAVING 
		COUNT(DISTINCT trimestre) = 4
),

ultimo_ano_completo AS (
	SELECT MAX(ano) AS ano
	FROM anos_completos
)

-- Agora, calcular as despesas totais por operadora no último ano completo
SELECT 
	op.registro_ans,
	op.razao_social,
	op.modalidade,
	SUM(ABS(dc.valor_conta)) AS valor_despesa_anual,
	(SELECT ano FROM ultimo_ano_completo) AS ano_referencia,
	COUNT(DISTINCT dc.trimestre) AS trimestres_incluidos
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimo_ano_completo uac ON dc.ano = uac.ano
WHERE 
	(
		dc.codigo_conta = '411111' 
		OR dc.codigo_conta LIKE '4111%'
		OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
		OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
	)
GROUP BY 
	op.registro_ans, op.razao_social, op.modalidade
ORDER BY 
	valor_despesa_anual DESC
LIMIT 10;

-- Método 2: Últimos 4 trimestres (independente do ano)
-- Identificar os últimos 4 trimestres disponíveis
WITH ultimos_trimestres AS (
	SELECT 
		ano,
		trimestre
	FROM (
		SELECT DISTINCT
			ano,
			trimestre,
			ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
		FROM demonstracoes_contabeis
	) t
	WHERE ordem <= 4
)

-- Calcular as despesas totais por operadora nos últimos 4 trimestres
SELECT 
	op.registro_ans,
	op.razao_social,
	op.modalidade,
	SUM(ABS(dc.valor_conta)) AS valor_despesa_ultimos_trimestres,
	CONCAT(
		'De ', 
		MIN(CONCAT(dc.ano, '-T', dc.trimestre)), 
		' a ', 
		MAX(CONCAT(dc.ano, '-T', dc.trimestre))
	) AS periodo,
	COUNT(DISTINCT CONCAT(dc.ano, dc.trimestre)) AS total_trimestres
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimos_trimestres ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
WHERE 
	(
		dc.codigo_conta = '411111' 
		OR dc.codigo_conta LIKE '4111%'
		OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
		OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
	)
GROUP BY 
	op.registro_ans, op.razao_social, op.modalidade
HAVING 
	total_trimestres = 4 -- Garantir que temos 4 trimestres para cada operadora
ORDER BY 
	valor_despesa_ultimos_trimestres DESC
LIMIT 10;

-- ----------------------------------------
-- Análises adicionais para interpretação dos resultados
-- ----------------------------------------

-- Verificar a distribuição das despesas por modalidade de operadora
WITH ultimo_trimestre AS (
	SELECT 
		ano, 
		trimestre
	FROM (
		SELECT 
			ano, 
			trimestre,
			ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
		FROM 
			demonstracoes_contabeis
		GROUP BY 
			ano, trimestre
	) t
	WHERE ordem = 1
)

SELECT 
	op.modalidade,
	COUNT(DISTINCT op.registro_ans) AS total_operadoras,
	SUM(ABS(dc.valor_conta)) AS valor_total_despesas,
	AVG(ABS(dc.valor_conta)) AS media_despesa_por_operadora
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimo_trimestre ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
WHERE 
	(
		dc.codigo_conta = '411111' 
		OR dc.codigo_conta LIKE '4111%'
		OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
		OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
	)
GROUP BY 
	op.modalidade
ORDER BY 
	valor_total_despesas DESC;

-- Analisar a evolução das despesas ao longo dos últimos 8 trimestres para as top 5 operadoras
WITH top_operadoras AS (
	-- Identificar as 5 operadoras com maiores despesas no último trimestre
	WITH ultimo_trimestre AS (
		SELECT 
			ano, 
			trimestre
		FROM (
			SELECT 
				ano, 
				trimestre,
				ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
			FROM 
				demonstracoes_contabeis
			GROUP BY 
				ano, trimestre
		) t
		WHERE ordem = 1
	)
	
	SELECT 
		op.registro_ans,
		op.razao_social,
		SUM(ABS(dc.valor_conta)) AS valor_despesa
	FROM 
		demonstracoes_contabeis dc
		JOIN operadoras op ON dc.registro_ans = op.registro_ans
		JOIN ultimo_trimestre ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
	WHERE 
		(
			dc.codigo_conta = '411111' 
			OR dc.codigo_conta LIKE '4111%'
			OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
			OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
		)
	GROUP BY 
		op.registro_ans, op.razao_social
	ORDER BY 
		valor_despesa DESC
	LIMIT 5
),

ultimos_trimestres AS (
	-- Selecionar os últimos 8 trimestres
	SELECT 
		ano,
		trimestre
	FROM (
		SELECT DISTINCT
			ano,
			trimestre,
			ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
		FROM demonstracoes_contabeis
	) t
	WHERE ordem <= 8
)

-- Mostrar a evolução trimestral
SELECT 
	op.registro_ans,
	op.razao_social,
	dc.ano,
	dc.trimestre,
	SUM(ABS(dc.valor_conta)) AS valor_despesa,
	CONCAT(dc.ano, '-T', dc.trimestre) AS periodo
FROM 
	demonstracoes_contabeis dc
	JOIN top_operadoras top ON dc.registro_ans = top.registro_ans
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimos_trimestres ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
WHERE 
	(
		dc.codigo_conta = '411111' 
		OR dc.codigo_conta LIKE '4111%'
		OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%ASSISTÊNCIA%SAÚDE MEDICO HOSPITALAR%'
		OR dc.descricao_conta LIKE '%EVENTOS/SINISTROS CONHECIDOS OU AVISADOS%'
	)
GROUP BY 
	op.registro_ans, op.razao_social, dc.ano, dc.trimestre, periodo
ORDER BY 
	op.registro_ans, dc.ano DESC, dc.trimestre DESC;

-- Calcular a sinistralidade das operadoras no último trimestre
WITH ultimo_trimestre AS (
	SELECT 
		ano, 
		trimestre
	FROM (
		SELECT 
			ano, 
			trimestre,
			ROW_NUMBER() OVER (ORDER BY ano DESC, trimestre DESC) AS ordem
		FROM 
			demonstracoes_contabeis
		GROUP BY 
			ano, trimestre
	) t
	WHERE ordem = 1
)

SELECT 
	op.registro_ans,
	op.razao_social,
	op.modalidade,
	-- Despesas com eventos/sinistros
	SUM(CASE 
			WHEN (dc.codigo_conta LIKE '411%' OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%') 
			THEN ABS(dc.valor_conta) 
			ELSE 0 
		END) AS despesas_assistenciais,
	
	-- Receitas com contraprestações
	SUM(CASE 
			WHEN (dc.codigo_conta LIKE '311%' OR dc.descricao_conta LIKE '%CONTRAPRESTAÇÃO%') 
			THEN ABS(dc.valor_conta) 
			ELSE 0 
		END) AS receitas_contraprestacoes,
	
	-- Cálculo da sinistralidade
	CASE
		WHEN SUM(CASE WHEN (dc.codigo_conta LIKE '311%' OR dc.descricao_conta LIKE '%CONTRAPRESTAÇÃO%') 
					  THEN ABS(dc.valor_conta) ELSE 0 END) > 0
		THEN ROUND(
				(SUM(CASE WHEN (dc.codigo_conta LIKE '411%' OR dc.descricao_conta LIKE '%EVENTOS%SINISTROS%') 
						  THEN ABS(dc.valor_conta) ELSE 0 END) /
				 SUM(CASE WHEN (dc.codigo_conta LIKE '311%' OR dc.descricao_conta LIKE '%CONTRAPRESTAÇÃO%') 
						  THEN ABS(dc.valor_conta) ELSE 0 END)) * 100, 2
			 )
		ELSE NULL
	END AS sinistralidade_percentual
FROM 
	demonstracoes_contabeis dc
	JOIN operadoras op ON dc.registro_ans = op.registro_ans
	JOIN ultimo_trimestre ut ON dc.ano = ut.ano AND dc.trimestre = ut.trimestre
WHERE 
	(
		dc.codigo_conta LIKE '411%' OR dc.codigo_conta LIKE '311%' OR
		dc.descricao_conta LIKE '%EVENTOS%SINISTROS%' OR dc.descricao_conta LIKE '%CONTRAPRESTAÇÃO%'
	)
GROUP BY 
	op.registro_ans, op.razao_social, op.modalidade
HAVING 
	receitas_contraprestacoes > 0 -- Filtrar apenas operadoras com receitas válidas
ORDER BY 
	sinistralidade_percentual DESC
LIMIT 20;