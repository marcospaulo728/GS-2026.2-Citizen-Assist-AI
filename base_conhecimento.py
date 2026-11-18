"""Classe BaseConhecimento: guarda as orientações em uma lista encadeada."""
from algoritmos import busca_sequencial_por_id, busca_sequencial_texto
from lista_encadeada import ListaEncadeada
from orientacao import Orientacao, PENDENTE
from utilitarios import carregar_json, salvar_json, isolar_arquivo, normalizar

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MIN_LETRAS_TITULO = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

CAMPOS_EDITAVEIS = ("categoria", "titulo", "palavras_chave", "resposta",
                    "documentos", "onde", "fonte", "verificado_em")

CRITERIOS_ORDENACAO = {
    "id": lambda o: o.id,
    "titulo": lambda o: normalizar(o.titulo),
    "categoria": lambda o: normalizar(o.categoria),
    "verificado_em": lambda o: o.verificado_em,
}


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = ListaEncadeada()   # lista encadeada de objetos Orientacao
        self.avisos = []

    # ----------------------------------------------------------- persistência
    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca levanta exceção.

        Devolve True se carregou ao menos uma orientação.
        """
        self.orientacoes = ListaEncadeada()
        self.avisos = []
        dados, status = carregar_json(self.caminho)
        if status == "ausente":
            self.avisos.append(f"Base não encontrada em '{self.caminho}'. "
                               "Iniciando com a base vazia.")
            return False
        if status in ("corrompido", "erro") or not isinstance(dados, list):
            isolar_arquivo(self.caminho)
            self.avisos.append("O arquivo da base está corrompido ou ilegível. "
                               "Ele foi guardado como '.corrompido' e a base começou vazia.")
            return False
        for posicao, item in enumerate(dados, start=1):
            try:
                orientacao = Orientacao.de_dict(item)
            except ValueError as erro:
                self.avisos.append(f"Registro {posicao} ignorado: {erro} "
                                   "(será removido do arquivo na próxima gravação).")
                continue
            if self.consultar(orientacao.id)[0] is not None:
                self.avisos.append(f"Registro {posicao} ignorado: ID {orientacao.id} repetido.")
                continue
            self.orientacoes.inserir_fim(orientacao)
        return len(self.orientacoes) > 0

    def salvar(self):
        """Grava a lista no JSON. Devolve True/False (nunca levanta exceção)."""
        try:
            salvar_json(self.caminho, [o.para_dict() for o in self.orientacoes])
            return True
        except OSError:
            return False

    # ------------------------------------------------------------- categorias
    def categorias(self):
        """Nomes das categorias, na ordem em que aparecem."""
        chaves, nomes = [], []
        for orientacao in self.orientacoes:
            chave = normalizar(orientacao.categoria)
            if chave not in chaves:
                chaves.append(chave)
                nomes.append(orientacao.categoria)
        return nomes

    def por_categoria(self, categoria):
        alvo = normalizar(categoria)
        return [o for o in self.orientacoes if normalizar(o.categoria) == alvo]

    def total_por_categoria(self):
        contagem, nomes = {}, {}
        for orientacao in self.orientacoes:
            chave = normalizar(orientacao.categoria)
            contagem[chave] = contagem.get(chave, 0) + 1
            nomes.setdefault(chave, orientacao.categoria)
        return {nomes[chave]: qtd for chave, qtd in contagem.items()}

    def pendentes(self):
        """Quantas orientações ainda estão com a verificação pendente."""
        return sum(1 for o in self.orientacoes if o.verificado_em == PENDENTE)

    # ------------------------------------------------------ busca por pontos
    def pontuar(self, orientacao, pergunta):
        """+3 por palavra-chave contida na pergunta; +1 por palavra (4+ letras) no título."""
        pergunta_norm = normalizar(pergunta)
        pontos = 0
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm.strip() and chave_norm in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE
        titulo_norm = normalizar(orientacao.titulo)
        vistas = set()
        for palavra in pergunta_norm.split():
            if len(palavra) >= MIN_LETRAS_TITULO and palavra not in vistas:
                vistas.add(palavra)
                if f" {palavra} " in titulo_norm:
                    pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        pergunta_norm = normalizar(pergunta)
        resultados = ListaEncadeada()
        for orientacao in self.orientacoes:
            pontos = self.pontuar(orientacao, pergunta_norm)
            if pontos > 0:
                resultados.inserir_fim((pontos, orientacao))
        resultados.ordenar(chave=lambda tupla: tupla[0], decrescente=True)
        return resultados.para_lista()

    @staticmethod
    def nivel_confianca(pontos):
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None

    # ----------------------------------------------------------------- CRUD
    def proximo_id(self):
        maior = 0
        for orientacao in self.orientacoes:
            if orientacao.id > maior:
                maior = orientacao.id
        return maior + 1

    def consultar(self, id_orientacao):
        """Devolve (orientacao ou None, comparacoes)."""
        return busca_sequencial_por_id(self.orientacoes, id_orientacao)

    def pesquisar(self, termo, campo):
        """Devolve (lista de orientações, comparacoes)."""
        return busca_sequencial_texto(self.orientacoes, termo, campo)

    def cadastrar(self, dados):
        """Valida e insere no fim. ValueError se inválido ou se o ID já existir."""
        orientacao = Orientacao.de_dict(dados)
        if self.consultar(orientacao.id)[0] is not None:
            raise ValueError(f"já existe uma orientação com o ID {orientacao.id}")
        self.orientacoes.inserir_fim(orientacao)
        return orientacao

    def atualizar(self, id_orientacao, campo, valor):
        """Altera um campo. Valida o registro inteiro ANTES de alterar o objeto."""
        if campo not in CAMPOS_EDITAVEIS:
            raise ValueError(f"o campo '{campo}' não pode ser alterado")
        orientacao, _ = self.consultar(id_orientacao)
        if orientacao is None:
            raise LookupError(f"não existe orientação com o ID {id_orientacao}")
        novos_dados = orientacao.para_dict()
        novos_dados[campo] = valor
        validada = Orientacao.de_dict(novos_dados)   # ValueError se inválido
        orientacao.copiar_de(validada)
        return orientacao

    def excluir(self, id_orientacao):
        """Remove da lista encadeada. LookupError se o ID não existir."""
        removida = self.orientacoes.remover(lambda o: o.id == id_orientacao)
        if removida is None:
            raise LookupError(f"não existe orientação com o ID {id_orientacao}")
        return removida

    def ordenar(self, criterio="id", decrescente=False):
        """Devolve uma CÓPIA da lista ordenada (Merge Sort); a original não muda."""
        if criterio not in CRITERIOS_ORDENACAO:
            raise ValueError(f"critério de ordenação inválido: {criterio}")
        copia = self.orientacoes.copiar()
        copia.ordenar(CRITERIOS_ORDENACAO[criterio], decrescente)
        return copia