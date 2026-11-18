"""Lista encadeada simples implementada pela equipe (nós e referências explícitas)."""


class No:
    """Um nó guarda um dado e a referência para o próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    """Lista com ponteiros para a cabeça e para a cauda."""

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0

    def __len__(self):
        return self.tamanho

    def esta_vazia(self):
        return self.cabeca is None

    # ------------------------------------------------------------- percurso
    def __iter__(self):
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def percorrer(self):
        """Percurso da lista, do primeiro ao último nó."""
        return iter(self)

    def para_lista(self):
        """Converte para list do Python (apenas para exibição e testes)."""
        return [dado for dado in self]

    # -------------------------------------------------------------- inserção
    def inserir_inicio(self, dado):
        """O(1)"""
        novo = No(dado)
        novo.proximo = self.cabeca
        self.cabeca = novo
        if self.cauda is None:
            self.cauda = novo
        self.tamanho += 1

    def inserir_fim(self, dado):
        """O(1), graças ao ponteiro para a cauda."""
        novo = No(dado)
        if self.cauda is None:
            self.cabeca = novo
        else:
            self.cauda.proximo = novo
        self.cauda = novo
        self.tamanho += 1

    # --------------------------------------------------------------- remoção
    def remover(self, predicado):
        """Remove o primeiro nó cujo dado satisfaz o predicado. O(n).

        Devolve o dado removido ou None se nada for encontrado.
        Trata remoção da cabeça, do meio, da cauda e do nó único.
        """
        anterior = None
        atual = self.cabeca
        while atual is not None:
            if predicado(atual.dado):
                if anterior is None:
                    self.cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.cauda:
                    self.cauda = anterior
                atual.proximo = None
                self.tamanho -= 1
                return atual.dado
            anterior = atual
            atual = atual.proximo
        return None

    def copiar(self):
        """Nova lista com novos nós apontando para os mesmos dados. O(n)."""
        copia = ListaEncadeada()
        for dado in self:
            copia.inserir_fim(dado)
        return copia

    # ------------------------------------------------------------ ordenação
    def ordenar(self, chave, decrescente=False):
        """Merge Sort sobre os nós (religa os ponteiros). O(n log n), estável."""
        if self.tamanho < 2:
            return
        self.cabeca = self._merge_sort(self.cabeca, chave, decrescente)
        atual = self.cabeca
        while atual.proximo is not None:
            atual = atual.proximo
        self.cauda = atual

    def _merge_sort(self, cabeca, chave, decrescente):
        if cabeca is None or cabeca.proximo is None:
            return cabeca
        esquerda, direita = self._dividir(cabeca)
        esquerda = self._merge_sort(esquerda, chave, decrescente)
        direita = self._merge_sort(direita, chave, decrescente)
        return self._intercalar(esquerda, direita, chave, decrescente)

    @staticmethod
    def _dividir(cabeca):
        """Divide ao meio com dois ponteiros (lento e rápido)."""
        lento = cabeca
        rapido = cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        meio = lento.proximo
        lento.proximo = None
        return cabeca, meio

    @staticmethod
    def _intercalar(esquerda, direita, chave, decrescente):
        """Une duas listas ordenadas. Em empate, leva o da esquerda (estável)."""
        sentinela = No(None)
        fim = sentinela
        while esquerda is not None and direita is not None:
            chave_e = chave(esquerda.dado)
            chave_d = chave(direita.dado)
            pegar_esquerda = (chave_e >= chave_d) if decrescente else (chave_e <= chave_d)
            if pegar_esquerda:
                fim.proximo = esquerda
                esquerda = esquerda.proximo
            else:
                fim.proximo = direita
                direita = direita.proximo
            fim = fim.proximo
        fim.proximo = esquerda if esquerda is not None else direita
        return sentinela.proximo