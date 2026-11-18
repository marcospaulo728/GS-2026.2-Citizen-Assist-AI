"""Algoritmos de busca sequencial sobre a lista encadeada (com contagem de comparações)."""
from utilitarios import normalizar


def busca_sequencial_por_id(lista, id_procurado):
    """Percorre nó a nó. Devolve (orientacao ou None, comparacoes). O(n)."""
    comparacoes = 0
    no = lista.cabeca
    while no is not None:
        comparacoes += 1
        if no.dado.id == id_procurado:
            return no.dado, comparacoes
        no = no.proximo
    return None, comparacoes


def _textos_do_campo(orientacao, campo):
    if campo == "palavras_chave":
        return [normalizar(palavra) for palavra in orientacao.palavras_chave]
    return [normalizar(getattr(orientacao, campo))]


def busca_sequencial_texto(lista, termo, campo):
    """Procura o termo (sem acentos/maiúsculas) em titulo, categoria ou palavras_chave.

    Devolve (lista_de_orientacoes, comparacoes). O(n * m), m = tamanho do texto.
    """
    termo_norm = normalizar(termo).strip()
    encontrados = []
    comparacoes = 0
    if not termo_norm:
        return encontrados, comparacoes
    no = lista.cabeca
    while no is not None:
        comparacoes += 1
        if any(termo_norm in texto for texto in _textos_do_campo(no.dado, campo)):
            encontrados.append(no.dado)
        no = no.proximo
    return encontrados, comparacoes