# Scripts Automação ANS

Este projeto contém a implementação de quatro etapas de uma automação:

1. Web Scraping
2. Transformação de Dados
3. Banco de Dados
4. API

## Arquivos do Projeto

- `1-webscraping_ans.py`: Script de web scraping para baixar anexos do site da ANS
- `2-transformacao-de-dados.py`: Script para extrair e transformar dados do PDF
- `3-download-ans-data.py`: Script para baixar dados de operadoras e demonstrações contábeis da ANS
- `4-create-tables-mysql.sql`: Script SQL para criar as tabelas no MySQL
- `5-import-data-mysql.sql`: Script SQL para importar os dados para o MySQL
- `6-analytical-queries.sql`: Consultas analíticas para responder as perguntas do teste
- `7-api-server.py`: Servidor API em Flask para consultas de operadoras
- `8-frontend/`: Pasta contendo a interface web em Vue.js
- `9-postman-collection.json`: Coleção Postman para testar a API

## Requisitos

### Python
- Python 3.8+
- Bibliotecas: requests, beautifulsoup4, zipfile, re, pandas, pdfplumber, flask, flask-cors, tqdm
  
Para instalar as dependências Python:
```bash
pip install requests beautifulsoup4 pandas pdfplumber flask flask-cors tqdm lxml mysql-connector-python
```

### Banco de Dados
- MySQL 8.0 ou PostgreSQL 10.0+

### Frontend
- Navegador web moderno

## Instruções de Execução

### 1. Web Scraping

Execute o script para baixar os anexos do site da ANS:

```bash
python 1-webscraping_ans.py
```

Isto irá:
- Acessar o site da ANS
- Baixar os Anexos I e II em formato PDF
- Compactar os anexos em um arquivo ZIP

### 2. Transformação de Dados

Execute o script para processar o PDF baixado:

```bash
python 2-transformacao-de-dados.py
```

Isto irá:
- Extrair os dados da tabela do Rol de Procedimentos do PDF
- Salvar os dados em formato CSV
- Substituir as abreviações por descrições completas
- Compactar o CSV em um arquivo ZIP

### 3. Banco de Dados

1. Primeiro, baixe os dados das demonstrações contábeis e operadoras:

```bash
python 3-download-ans-data.py
```

2. Execute o script que cria o banco de dados e importa as informações:

```bash
python 7-execute-scripts-database.py
```

### 4. API

1. Execute o servidor API:

```bash
python 8-api-server.py
```

2. Abra o arquivo `9-frontend/index.html` em seu navegador.

3. Importe a coleção `10-postman-collection.json` no Postman para testar a API.

## Estrutura do Projeto

```
projeto/
├── downloads_ans/       # Diretório para os arquivos baixados da ANS
├── dados_ans/           # Diretório para os dados das operadoras e demonstrações
│   ├── operadoras_ativas/
│   └── demonstracoes_contabeis/
├── 1-webscraping_ans.py
├── 2-transformacao-de-dados.py
├── 3-download-ans-data.py
├── 4-create-tables-mysql.sql
├── 5-import-data-mysql.sql
├── 6-analytical-queries.sql
├── 7-execute-scripts-database.py
├── 8-api-server.py
├── 9-frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── 10-postman-collection.json
```

## Observações

- Certifique-se de ajustar os caminhos dos arquivos nos scripts SQL conforme necessário
- O servidor API está configurado para rodar na porta 5000, verifique se essa porta está disponível
- Para o frontend acessar a API, você precisa ter o servidor rodando localmente
