"""Telas de gestão da base (DSA): CRUD, pesquisa, ordenação e análise."""
from utilitarios import (entrada, ler_opcao, ler_sn, ler_texto, lista_por_virgulas)

CAMPOS_MENU = [
    ("categoria", "Categoria"),
    ("titulo", "Título"),
    ("palavras_chave", "Palavras-chave (substitui todas)"),
    ("resposta", "Resposta"),
    ("documentos", "Documentos (substitui todos)"),
    ("onde", "Onde"),
    ("fonte", "Fonte (URL oficial)"),
    ("verificado_em", "Data de verificação (AAAA-MM-DD)"),
]
CAMPOS_PESQUISA = [("titulo", "Título"), ("categoria", "Categoria"),
                   ("palavras_chave", "Palavra-chave")]
CRITERIOS = [("id", "ID"), ("titulo", "Título (A-Z)"), ("categoria", "Categoria"),
             ("verificado_em", "Data de verificação")]


class Gestao:
    def __init__(self, base):
        self.base = base

    # --------------------------------------------------------------- apoio
    def _persistir(self):
        if self.base.salvar():
            print("Alteração gravada em disco.")
        else:
            print("Aviso: não foi possível gravar o arquivo. A alteração está só na memória.")

    def _base_vazia(self):
        if len(self.base.orientacoes) == 0:
            print("A base está vazia. Use a opção 3 para cadastrar uma orientação.")
            return True
        return False

    def _pedir_orientacao(self, mensagem):
        """Pede um ID até achar um existente. Devolve a orientação ou None (voltar)."""
        if self._base_vazia():
            return None
        while True:
            texto = ler_texto(f"{mensagem} (0 para voltar): ")
            if texto is None:
                return None
            if not texto.isdecimal():
                print("ID inválido. Digite apenas números.")
                continue
            orientacao, comparacoes = self.base.consultar(int(texto))
            if orientacao is None:
                print(f"Nenhuma orientação com ID {texto} ({comparacoes} comparações).")
                continue
            self.ultimas_comparacoes = comparacoes
            return orientacao

    @staticmethod
    def _imprimir_tabela(lista):
        print(f"\n{'ID':>3}  {'Categoria':<12} {'Título':<52} Verificado em")
        for o in lista:
            print(f"{o.id:>3}  {o.categoria[:12]:<12} {o.titulo[:52]:<52} {o.verificado_em}")

    # ------------------------------------------------------------- cadastro
    def cadastrar(self):
        print("\n--- Cadastrar orientação (digite 0 em qualquer campo para cancelar) ---")
        sugestao = self.base.proximo_id()
        while True:
            bruto = entrada(f"ID (Enter = {sugestao}): ").strip()
            if bruto == "0":
                return
            if bruto == "":
                id_novo = sugestao
            elif bruto.isdecimal() and int(bruto) > 0:
                id_novo = int(bruto)
            else:
                print("ID inválido. Use um número inteiro positivo.")
                continue
            if self.base.consultar(id_novo)[0] is not None:
                print(f"Já existe uma orientação com o ID {id_novo}. Escolha outro.")
                continue
            break
        existentes = ", ".join(self.base.categorias()) or "nenhuma ainda"
        categoria = ler_texto(f"Categoria (existentes: {existentes}): ")
        if categoria is None:
            return
        titulo = ler_texto("Título: ")
        if titulo is None:
            return
        palavras = ler_texto("Palavras-chave separadas por vírgula (mínimo 3): ")
        if palavras is None:
            return
        resposta = ler_texto("Resposta em linguagem simples: ")
        if resposta is None:
            return
        documentos = ler_texto("Documentos separados por vírgula (Enter se nenhum): ",
                               permitir_vazio=True)
        if documentos is None:
            return
        onde = ler_texto("Onde ir: ")
        if onde is None:
            return
        fonte = ler_texto("Fonte oficial (URL começando com http): ")
        if fonte is None:
            return
        verificado = ler_texto("Data em que a equipe conferiu (AAAA-MM-DD): ")
        if verificado is None:
            return
        dados = {"id": id_novo, "categoria": categoria, "titulo": titulo,
                 "palavras_chave": lista_por_virgulas(palavras), "resposta": resposta,
                 "documentos": lista_por_virgulas(documentos), "onde": onde,
                 "fonte": fonte, "verificado_em": verificado}
        try:
            orientacao = self.base.cadastrar(dados)
        except ValueError as erro:
            print(f"Cadastro recusado: {erro}.")
            return
        self._persistir()
        print(f"Orientação {orientacao.id} cadastrada. Total na base: {len(self.base.orientacoes)}.")

    # ------------------------------------------------------------- consulta
    def consultar(self):
        orientacao = self._pedir_orientacao("ID da orientação")
        if orientacao is None:
            return
        print()
        orientacao.exibir()
        print(f"\n(Busca sequencial: {self.ultimas_comparacoes} comparação(ões) "
              f"em uma lista de {len(self.base.orientacoes)} nó(s).)")

    # ------------------------------------------------------------- pesquisa
    def pesquisar(self):
        if self._base_vazia():
            return
        print("\nPesquisar por:")
        for numero, (_, rotulo) in enumerate(CAMPOS_PESQUISA, start=1):
            print(f"  {numero}. {rotulo}")
        print("  0. Voltar")
        escolha = ler_opcao("Escolha: ", 0, len(CAMPOS_PESQUISA))
        if escolha == 0:
            return
        campo = CAMPOS_PESQUISA[escolha - 1][0]
        termo = ler_texto("Termo de busca (0 para voltar): ")
        if termo is None:
            return
        resultados, comparacoes = self.base.pesquisar(termo, campo)
        if not resultados:
            print(f"Nenhuma orientação encontrada para '{termo}' ({comparacoes} comparações).")
            return
        print(f"{len(resultados)} resultado(s) ({comparacoes} comparações):")
        self._imprimir_tabela(resultados)

    # ------------------------------------------------------------ atualizar
    def atualizar(self):
        orientacao = self._pedir_orientacao("ID da orientação a atualizar")
        if orientacao is None:
            return
        print()
        orientacao.exibir()
        print("\nO que deseja alterar? (o ID não pode ser alterado)")
        for numero, (_, rotulo) in enumerate(CAMPOS_MENU, start=1):
            print(f"  {numero}. {rotulo}")
        print("  9. Adicionar uma palavra-chave")
        print("  0. Voltar")
        escolha = ler_opcao("Escolha: ", 0, 9)
        if escolha == 0:
            return
        if escolha == 9:
            campo = "palavras_chave"
            nova = ler_texto("Nova palavra-chave (0 cancela): ")
            if nova is None:
                return
            valor = list(orientacao.palavras_chave) + [nova]
        else:
            campo = CAMPOS_MENU[escolha - 1][0]
            texto = ler_texto("Novo valor (0 cancela): ",
                              permitir_vazio=(campo == "documentos"))
            if texto is None:
                return
            valor = lista_por_virgulas(texto) if campo in ("palavras_chave", "documentos") else texto
        try:
            self.base.atualizar(orientacao.id, campo, valor)
        except (ValueError, LookupError) as erro:
            print(f"Atualização recusada: {erro}. Nada foi alterado.")
            return
        self._persistir()
        print("Orientação atualizada:\n")
        orientacao.exibir()

    # -------------------------------------------------------------- excluir
    def excluir(self):
        orientacao = self._pedir_orientacao("ID da orientação a excluir")
        if orientacao is None:
            return
        if not ler_sn(f"Excluir '{orientacao.titulo}'? (s/n): "):
            print("Exclusão cancelada.")
            return
        try:
            self.base.excluir(orientacao.id)
        except LookupError as erro:
            print(f"Não foi possível excluir: {erro}.")
            return
        self._persistir()
        print(f"Orientação excluída. Total na base: {len(self.base.orientacoes)}.")
        if len(self.base.orientacoes) < 10:
            print("Atenção: a base ficou com menos de 10 orientações (mínimo exigido em PCP).")

    # ------------------------------------------------------------- ordenar
    def ordenar_listar(self):
        if self._base_vazia():
            return
        print("\nOrdenar por:")
        for numero, (_, rotulo) in enumerate(CRITERIOS, start=1):
            print(f"  {numero}. {rotulo}")
        print("  0. Voltar")
        escolha = ler_opcao("Escolha: ", 0, len(CRITERIOS))
        if escolha == 0:
            return
        print("  1. Crescente\n  2. Decrescente")
        sentido = ler_opcao("Ordem: ", 1, 2)
        lista = self.base.ordenar(CRITERIOS[escolha - 1][0], decrescente=(sentido == 2))
        print(f"\nOrdenado com Merge Sort por: {CRITERIOS[escolha - 1][1]}")
        self._imprimir_tabela(lista)

    # -------------------------------------------------------------- análise
    def analise(self):
        total = len(self.base.orientacoes)
        print("\n--- Análise da base (lista encadeada) ---")
        print(f"Total de orientações: {total}")
        if total == 0:
            print("A base está vazia.")
            return
        print("Quantidade por categoria:")
        for categoria, quantidade in self.base.total_por_categoria().items():
            print(f"  - {categoria}: {quantidade}")
        print(f"Orientações com verificação pendente: {self.base.pendentes()}")
        if total < 10:
            print("Atenção: menos de 10 orientações (mínimo exigido em PCP).")
        print("Complexidade (n = nº de orientações): inserir no fim O(1) | "
              "buscar O(n) | remover O(n) | ordenar (Merge Sort) O(n log n)")