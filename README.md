# Webscraping ANS - Download de Anexos

Este projeto realiza webscraping no site da Agência Nacional de Saúde Suplementar (ANS) para automatizar o download dos Anexos I e II em formato PDF e compactá-los em um único arquivo.

## Funcionalidades

- Acessa o site da ANS: [Atualização do Rol de Procedimentos](https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos)
- Localiza e baixa os Anexos I e II em formato PDF
- Compacta todos os anexos em um único arquivo ZIP
- Salva o HTML da página para análise e depuração

## Requisitos

- Python 3.6 ou superior
- Bibliotecas:
  - requests
  - beautifulsoup4
  - zipfile (biblioteca padrão)
  - re (biblioteca padrão)
  - urllib (biblioteca padrão)

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/leonardonogueiramo/web-scraping-download-anexo-python.git
cd webscraping-ans
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

Ou instale manualmente:
```bash
pip install requests beautifulsoup4
```

## Uso

Execute o script principal:

```bash
python webscraping_ans.py
```

Os arquivos serão baixados para a pasta `downloads_ans` e compactados em `downloads_ans/anexos_ans.zip`.

## Estrutura do Projeto

```
webscraping-ans/
│
├── webscraping_ans.py     # Script principal
├── downloads_ans/         # Pasta onde os anexos são salvos
├── pagina_ans.html        # HTML da página para debug
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo
```

## Como Funciona

1. O script faz uma requisição HTTP ao site da ANS
2. Analisa o HTML da página usando BeautifulSoup 
3. Busca links que contenham referências aos Anexos I e II
4. Baixa os arquivos PDF encontrados
5. Compacta os arquivos em um único ZIP

## Resolução de Problemas

Se o script não encontrar os anexos, algumas possíveis causas são:

- Alterações na estrutura do site da ANS
- Bloqueio de requisições automatizadas
- Carregamento dinâmico de conteúdo via JavaScript

Em caso de problemas, verifique o arquivo `pagina_ans.html` gerado para entender a estrutura atual da página.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Aviso Legal

Este projeto foi criado apenas para fins educacionais e de automação de tarefas. Certifique-se de respeitar os termos de uso do site da ANS ao utilizar este script.