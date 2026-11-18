"""Citizen Assist AI: ponto de entrada. Execute com:  python main.py"""
import os
import sys

from assistente import Assistente
from base_conhecimento import BaseConhecimento
from gestao import Gestao
from utilitarios import ler_opcao

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")

MENU = """
========== CITIZEN ASSIST AI ==========
  1. Tirar uma dúvida (texto livre)
  2. Navegar por categorias
  3. Cadastrar orientação
  4. Consultar orientação por ID
  5. Pesquisar orientações
  6. Atualizar orientação
  7. Excluir orientação
  8. Listar orientações ordenadas
  9. Análise e indicadores
 10. Exportar atendimentos para CSV
  0. Sair
======================================="""


def configurar_terminal():
    for fluxo in (sys.stdout, sys.stdin):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def pedir_nota(assistente):
    print("\nAntes de sair: de 1 a 5, qual a facilidade de usar este assistente?")
    print("(1 = muito difícil, 5 = muito fácil)")
    nota = ler_opcao("Nota (0 para pular): ", 0, 5)
    if nota:
        assistente.registrar_nota(nota)
        print("Obrigado pela avaliação!")


def main():
    configurar_terminal()
    base = BaseConhecimento(CAMINHO_BASE)
    base.carregar()
    for aviso in base.avisos:
        print("Aviso:", aviso)
    if base.pendentes():
        print(f"Aviso: {base.pendentes()} orientação(ões) com a data de verificação PENDENTE.")

    assistente = Assistente("Citizen Assist AI", base)
    gestao = Gestao(base)
    print(f"\nBem-vindo ao {assistente.nome}!")
    print("Este assistente NÃO é um canal oficial e nunca pede dados pessoais.")

    acoes = {
        1: assistente.perguntar,
        2: assistente.navegar,
        3: gestao.cadastrar,
        4: gestao.consultar,
        5: gestao.pesquisar,
        6: gestao.atualizar,
        7: gestao.excluir,
        8: gestao.ordenar_listar,
        9: lambda: (gestao.analise(), assistente.exibir_indicadores()),
        10: assistente.exportar_csv,
    }
    try:
        while True:
            print(MENU)
            opcao = ler_opcao("Escolha uma opção: ", 0, 10)
            if opcao == 0:
                break
            acoes[opcao]()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrando...")

    try:
        pedir_nota(assistente)
    except (KeyboardInterrupt, EOFError):
        print()
    assistente.exportar_csv()
    print("Até logo!")


if __name__ == "__main__":
    main()