"""Funções de apoio usadas por todos os módulos."""
import json
import os
from datetime import datetime

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação, com um espaço em cada ponta."""
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def contem_dado_pessoal(texto):
    """True se o texto tiver 8 ou mais dígitos ou o caractere @."""
    digitos = sum(1 for caractere in texto if caractere.isdigit())
    return digitos >= 8 or "@" in texto


def data_valida(texto):
    """True se o texto estiver no formato AAAA-MM-DD e for uma data real."""
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def lista_por_virgulas(texto):
    """'a, b,, c' -> ['a', 'b', 'c']"""
    return [parte.strip() for parte in texto.split(",") if parte.strip()]


# ---------------------------------------------------------------- entradas
def entrada(mensagem):
    """input() isolado em um ponto só (EOF/Ctrl+C são tratados no main)."""
    return input(mensagem)


def ler_texto(mensagem, permitir_vazio=False):
    """Devolve o texto digitado, ou None se a pessoa digitar 0 (voltar)."""
    while True:
        valor = entrada(mensagem).strip()
        if valor == "0":
            return None
        if valor or permitir_vazio:
            return valor
        print("Entrada vazia. Digite algo ou 0 para voltar.")


def ler_opcao(mensagem, minimo, maximo):
    """Pede um número inteiro entre minimo e maximo, repetindo se for inválido."""
    while True:
        valor = entrada(mensagem).strip()
        if valor.isdecimal() and minimo <= int(valor) <= maximo:
            return int(valor)
        print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")


def ler_sn(mensagem):
    """Pede s/n e devolve True ou False."""
    while True:
        valor = normalizar(entrada(mensagem)).strip()
        if valor in ("s", "sim"):
            return True
        if valor in ("n", "nao"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


# ----------------------------------------------------------------- arquivos
def carregar_json(caminho):
    """Devolve (dados, status). Status: 'ok', 'ausente', 'corrompido' ou 'erro'."""
    if not os.path.exists(caminho):
        return None, "ausente"
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo), "ok"
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "corrompido"
    except OSError:
        return None, "erro"


def salvar_json(caminho, dados):
    """Grava em arquivo temporário e renomeia (evita deixar o JSON pela metade)."""
    pasta = os.path.dirname(os.path.abspath(caminho))
    os.makedirs(pasta, exist_ok=True)
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)


def isolar_arquivo(caminho):
    """Renomeia um arquivo ilegível para .corrompido, preservando o conteúdo."""
    try:
        os.replace(caminho, caminho + ".corrompido")
        return True
    except OSError:
        return False