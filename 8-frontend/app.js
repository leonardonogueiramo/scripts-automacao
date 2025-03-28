// Aplicação Vue.js para consulta de operadoras ANS

// Configuração da URL base da API
const API_BASE_URL = 'http://localhost:5000/api';

// Instância principal do Vue
new Vue({
	el: '#app',
	data: {
		// Estado da aplicação
		termoBusca: '',
		resultados: [],
		totalResultados: 0,
		carregando: false,
		erro: null,
		buscaRealizada: false,
		
		// Configurações
		limite: 10,
		
		// Modal de detalhes
		operadoraSelecionada: null,
		modalDetalhes: null,
		
		// Data para footer
		anoAtual: new Date().getFullYear()
	},
	
	// Lifecycle hook - quando o componente é montado
	mounted() {
		// Inicializar o modal do Bootstrap
		this.modalDetalhes = new bootstrap.Modal(document.getElementById('detalhesModal'));
		
		// Verificar status da API ao carregar a página
		this.verificarStatusAPI();
	},
	
	// Métodos da aplicação
	methods: {
		// Buscar operadoras baseado no termo de busca
		buscarOperadoras() {
			// Verificar se há um termo de busca
			if (!this.termoBusca.trim()) {
				this.erro = "Por favor, digite um termo para busca.";
				return;
			}
			
			// Limpar erro anterior
			this.erro = null;
			
			// Indicar que está carregando
			this.carregando = true;
			
			// Construir URL da API com parâmetros
			const url = `${API_BASE_URL}/operadoras/busca?termo=${encodeURIComponent(this.termoBusca)}&limite=${this.limite}`;
			
			// Fazer requisição à API
			axios.get(url)
				.then(response => {
					// Processar resposta
					this.resultados = response.data.resultados || [];
					this.totalResultados = response.data.total || 0;
					this.buscaRealizada = true;
				})
				.catch(error => {
					console.error('Erro na busca:', error);
					this.erro = "Ocorreu um erro ao buscar as operadoras. Por favor, tente novamente.";
					if (error.response && error.response.data && error.response.data.erro) {
						this.erro = error.response.data.erro;
					}
					this.resultados = [];
					this.totalResultados = 0;
				})
				.finally(() => {
					this.carregando = false;
				});
		},
		
		// Exibir detalhes de uma operadora
		exibirDetalhes(operadora) {
			this.operadoraSelecionada = operadora;
			this.modalDetalhes.show();
		},
		
		// Verificar status da API
		verificarStatusAPI() {
			axios.get(`${API_BASE_URL}/status`)
				.then(response => {
					if (!response.data.dados_carregados) {
						console.warn('API está online, mas os dados não estão carregados.');
					}
				})
				.catch(error => {
					console.error('Erro ao verificar status da API:', error);
					this.erro = "Não foi possível conectar ao servidor da API. Verifique se o servidor está em execução.";
				});
		},
		
		// Formatar valores para exibição
		formatarCNPJ(cnpj) {
			if (!cnpj) return '-';
			
			// Formatar CNPJ: XX.XXX.XXX/XXXX-XX
			return cnpj.replace(
				/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
				"$1.$2.$3/$4-$5"
			);
		},
		
		formatarCEP(cep) {
			if (!cep) return '-';
			
			// Formatar CEP: XXXXX-XXX
			return cep.replace(/^(\d{5})(\d{3})$/, "$1-$2");
		},
		
		formatarTelefone(telefone) {
			if (!telefone) return '-';
			
			// Formatar telefone
			if (telefone.length === 8) {
				return `${telefone.substring(0, 4)}-${telefone.substring(4)}`;
			} else if (telefone.length === 9) {
				return `${telefone.substring(0, 5)}-${telefone.substring(5)}`;
			} else {
				return telefone;
			}
		}
	}
});