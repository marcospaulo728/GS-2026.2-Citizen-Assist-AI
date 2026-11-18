"""Classe Assistente: atendimento, histórico, indicadores e exportação CSV."""
import csv
import os
import time
from datetime import datetime

from base_conhecimento import BaseConhecimento, LIMITE_MEDIA
from utilitarios import (carregar_json, contem_dado_pessoal, isolar_arquivo,
                         ler_opcao, ler_sn, ler_texto, salvar_json)

CAMPOS_ATENDIMENTO = ["data", "origem", "pergunta", "id_orientacao",
                      "encontrou", "ajudou", "tentativas", "tempo_segundos"]


def _numero(valor, padrao=0.0):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base                      # composição: Assistente tem uma BaseConhecimento
        pasta = os.path.dirname(os.path.abspath(base.caminho))
        self.caminho_historico = os.path.join(pasta, "historico.json")
        self.caminho_avaliacoes = os.path.join(pasta, "avaliacoes.json")
        self.caminho_csv = os.path.join(pasta, "atendimentos.csv")
        self.historico = self._carregar_lista(self.caminho_historico,
                                              CAMPOS_ATENDIMENTO, "o histórico")
        self.avaliacoes = self._carregar_lista(self.caminho_avaliacoes,
                                               ["data", "nota"], "as avaliações")

    # ------------------------------------------------------------ arquivos
    @staticmethod
    def _carregar_lista(caminho, obrigatorios, rotulo):
        dados, status = carregar_json(caminho)
        if status == "ausente":
            return []
        if status != "ok" or not isinstance(dados, list):
            isolar_arquivo(caminho)
            print(f"Aviso: não foi possível ler {rotulo}. Começando vazio "
                  "(o arquivo antigo foi guardado como '.corrompido').")
            return []
        return [item for item in dados
                if isinstance(item, dict) and all(c in item for c in obrigatorios)]

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        """Guarda um atendimento e grava data/historico.json."""
        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta[:200],
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
        })
        try:
            salvar_json(self.caminho_historico, self.historico)
        except OSError:
            print("Aviso: não foi possível gravar o histórico em arquivo.")

    def registrar_nota(self, nota):
        self.avaliacoes.append({"data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "nota": nota})
        try:
            salvar_json(self.caminho_avaliacoes, self.avaliacoes)
        except OSError:
            print("Aviso: não foi possível gravar a avaliação.")

    # --------------------------------------------------------- atendimento
    def perguntar(self):
        """Atendimento por texto livre. Cada dúvida resolvida (ou abandonada) é um atendimento."""
        if len(self.base.orientacoes) == 0:
            print("A base de conhecimento está vazia. Cadastre orientações (opção 3).")
            return
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        ultimo_id = None
        encontrou = False
        while True:
            texto = ler_texto("\nDigite sua dúvida (0 para voltar): ")
            if texto is None:
                if tentativas > 0:       # dúvida abandonada: registra como sem solução
                    self.registrar("pergunta", ultima_pergunta, ultimo_id, encontrou,
                                   False, tentativas, round(time.time() - inicio, 1))
                return
            if contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue                  # não conta tentativa e não é registrado
            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)
            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                self._mostrar_nao_encontrei()
                continue
            pontos, melhor = resultados[0]
            encontrou = True
            ultimo_id = melhor.id
            nivel = self.base.nivel_confianca(pontos)
            print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)\n")
            melhor.exibir()
            alternativas = [(p, o) for p, o in resultados[1:3] if p >= 1]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} [{o.categoria}] ({p} pontos)")
            ajudou = ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                self.registrar("pergunta", texto, melhor.id, True, True, tentativas,
                               round(time.time() - inicio, 1))
                inicio = time.time()
                tentativas = 0
                ultima_pergunta = ""
                ultimo_id = None
                encontrou = False
            else:
                print("Tudo bem. Reescreva a dúvida com outras palavras ou digite 0 para voltar.")

    def _mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        exemplos = []
        for orientacao in self.base.orientacoes:
            if len(exemplos) == 3:
                break
            exemplos.append(orientacao.palavras_chave[0])
        print("Tente outras palavras (por exemplo: " + ", ".join(exemplos) + ")")
        print("ou navegue pelas categorias: " + ", ".join(self.base.categorias()) + " (menu, opção 2).")

    def navegar(self):
        """Navegação por categorias, com 0 para voltar em todas as telas."""
        while True:
            categorias = self.base.categorias()
            if not categorias:
                print("Não há categorias: a base está vazia.")
                return
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            escolha = ler_opcao("Escolha a categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        while True:
            orientacoes = self.base.por_categoria(categoria)
            if not orientacoes:
                print("Esta categoria ficou sem orientações.")
                return
            print(f"\nOrientações em {categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")
            inicio = time.time()
            escolha = ler_opcao("Escolha a orientação: ", 0, len(orientacoes))
            if escolha == 0:
                return
            orientacao = orientacoes[escolha - 1]
            print()
            orientacao.exibir()
            ajudou = ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", orientacao.titulo, orientacao.id, True, ajudou,
                           1, round(time.time() - inicio, 1))

    # ---------------------------------------------------------- indicadores
    def indicadores(self):
        total = len(self.historico)
        encontrados = [h for h in self.historico if h.get("encontrou") is True]
        ajudaram = [h for h in self.historico if h.get("ajudou") is True]
        tempos = [_numero(h.get("tempo_segundos")) for h in encontrados]
        tentativas = [_numero(h.get("tentativas")) for h in self.historico]
        notas = [_numero(a.get("nota")) for a in self.avaliacoes]
        sem_solucao = []
        for h in self.historico:
            if h.get("encontrou") is not True or h.get("ajudou") is not True:
                texto = str(h.get("pergunta", "")).strip()
                if texto and texto not in sem_solucao:
                    sem_solucao.append(texto)
        return {
            "total": total,
            "resposta_encontrada_pct": (100 * len(encontrados) / total) if total else 0.0,
            "acerto_pct": (100 * len(ajudaram) / total) if total else 0.0,
            "tempo_medio": (sum(tempos) / len(tempos)) if tempos else None,
            "tentativas_media": (sum(tentativas) / total) if total else None,
            "facilidade_media": (sum(notas) / len(notas)) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def exibir_indicadores(self):
        ind = self.indicadores()
        print("\n--- Indicadores de atendimento ---")
        print(f"Atendimentos registrados: {ind['total']}")
        if ind["total"] == 0:
            print("Ainda não há atendimentos. Use as opções 1 ou 2 do menu.")
            return
        print(f"Resposta encontrada (%): {ind['resposta_encontrada_pct']:.1f}")
        print(f"Taxa de acerto: ajudou (%): {ind['acerto_pct']:.1f}")
        tempo = ind["tempo_medio"]
        print("Tempo médio para encontrar: "
              + (f"{tempo:.1f} s" if tempo is not None else "sem dados"))
        print(f"Tentativas por atendimento: {ind['tentativas_media']:.1f}")
        facilidade = ind["facilidade_media"]
        print("Facilidade de uso (1 a 5): "
              + (f"{facilidade:.1f}" if facilidade is not None else "sem notas ainda"))
        if ind["sem_solucao"]:
            print("Dúvidas sem solução:")
            for texto in ind["sem_solucao"]:
                print(f"  - {texto}")
        else:
            print("Dúvidas sem solução: nenhuma")

    # ------------------------------------------------------------------ CSV
    def exportar_csv(self):
        """Exporta o histórico para data/atendimentos.csv com csv.DictWriter."""
        try:
            os.makedirs(os.path.dirname(self.caminho_csv), exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_ATENDIMENTO,
                                          extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"CSV exportado: {self.caminho_csv} ({len(self.historico)} atendimentos)")
            return True
        except OSError as erro:
            print(f"Não foi possível exportar o CSV ({erro}). "
                  "Se o arquivo estiver aberto em outro programa, feche-o e tente de novo.")
            return False