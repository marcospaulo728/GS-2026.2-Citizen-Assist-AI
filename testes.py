"""Testes automatizados. Execute com:  python testes.py   (ou: python -m unittest testes -v)"""
import csv
import os
import shutil
import tempfile
import unittest

from assistente import Assistente
from base_conhecimento import BaseConhecimento
from lista_encadeada import ListaEncadeada
from orientacao import Orientacao
from utilitarios import contem_dado_pessoal, normalizar


def dados(id_, categoria="Teste", titulo="Titulo de teste", chaves=None):
    return {"id": id_, "categoria": categoria, "titulo": titulo,
            "palavras_chave": chaves or ["alfa", "beta", "gama"],
            "resposta": "Resposta", "documentos": ["Doc"], "onde": "Local",
            "fonte": "https://www.gov.br", "verificado_em": "2026-01-01"}


class TestListaEncadeada(unittest.TestCase):
    def montar(self, valores):
        lista = ListaEncadeada()
        for valor in valores:
            lista.inserir_fim(valor)
        return lista

    def test_inserir_e_percorrer(self):
        lista = self.montar([1, 2, 3])
        lista.inserir_inicio(0)
        self.assertEqual(lista.para_lista(), [0, 1, 2, 3])
        self.assertEqual(len(lista), 4)

    def test_remover_cabeca_meio_cauda(self):
        lista = self.montar([1, 2, 3, 4])
        self.assertEqual(lista.remover(lambda x: x == 1), 1)
        self.assertEqual(lista.remover(lambda x: x == 3), 3)
        self.assertEqual(lista.remover(lambda x: x == 4), 4)
        self.assertEqual(lista.para_lista(), [2])
        lista.inserir_fim(9)                      # a cauda deve ter sido atualizada
        self.assertEqual(lista.para_lista(), [2, 9])

    def test_remover_unico_e_inexistente(self):
        lista = self.montar([5])
        self.assertIsNone(lista.remover(lambda x: x == 7))
        self.assertEqual(lista.remover(lambda x: x == 5), 5)
        self.assertTrue(lista.esta_vazia())
        lista.inserir_fim(6)
        self.assertEqual(lista.para_lista(), [6])

    def test_lista_vazia(self):
        lista = ListaEncadeada()
        self.assertEqual(lista.para_lista(), [])
        self.assertIsNone(lista.remover(lambda x: True))
        lista.ordenar(lambda x: x)                # não deve falhar
        self.assertEqual(len(lista), 0)

    def test_ordenar_crescente_decrescente(self):
        lista = self.montar([5, 1, 4, 2, 3])
        lista.ordenar(lambda x: x)
        self.assertEqual(lista.para_lista(), [1, 2, 3, 4, 5])
        lista.ordenar(lambda x: x, decrescente=True)
        self.assertEqual(lista.para_lista(), [5, 4, 3, 2, 1])
        lista.inserir_fim(0)                      # cauda correta após ordenar
        self.assertEqual(lista.para_lista()[-1], 0)

    def test_ordenar_e_estavel(self):
        lista = self.montar([(1, "a"), (1, "b"), (0, "c")])
        lista.ordenar(lambda t: t[0])
        self.assertEqual(lista.para_lista(), [(0, "c"), (1, "a"), (1, "b")])
        lista.ordenar(lambda t: t[0], decrescente=True)
        self.assertEqual(lista.para_lista(), [(1, "a"), (1, "b"), (0, "c")])


class TestBuscaEPontuacao(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar("  Como FAÇO o Cartão?  "), " como faco o cartao ")

    def test_dado_pessoal(self):
        self.assertTrue(contem_dado_pessoal("meu cpf é 123.456.789-00"))
        self.assertTrue(contem_dado_pessoal("escreva para ana@email.com"))
        self.assertFalse(contem_dado_pessoal("tenho 18 anos"))

    def test_pontuacao_exemplo_do_enunciado(self):
        base = BaseConhecimento("nao_usado.json")
        sus = Orientacao.de_dict(dados(
            3, "Saúde", "Fazer o Cartão Nacional de Saúde (Cartão SUS)",
            ["cartao sus", "cartao do sus", "sus", "cns"]))
        self.assertEqual(base.pontuar(sus, "Como faço o cartão do SUS?"), 7)
        self.assertEqual(base.nivel_confianca(7), "ALTA")
        self.assertEqual(base.nivel_confianca(3), "MÉDIA")
        self.assertIsNone(base.nivel_confianca(2))

    def test_buscar_devolve_tuplas_em_ordem_decrescente(self):
        base = BaseConhecimento("nao_usado.json")
        base.cadastrar(dados(1, titulo="Outro assunto", chaves=["zeta", "eta", "teta"]))
        base.cadastrar(dados(2, titulo="Passaporte brasileiro",
                             chaves=["passaporte", "pedir passaporte", "viagem"]))
        resultados = base.buscar("quero pedir passaporte")
        self.assertEqual(resultados[0][1].id, 2)
        self.assertEqual(resultados[0][0], 7)
        pontos = [p for p, _ in resultados]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertEqual(base.buscar("assunto totalmente diferente xyz"), [])


class TestBase(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pasta, True)
        self.caminho = os.path.join(self.pasta, "base.json")
        self.base = BaseConhecimento(self.caminho)

    def test_cadastrar_duplicado(self):
        self.base.cadastrar(dados(1))
        with self.assertRaises(ValueError):
            self.base.cadastrar(dados(1))
        self.assertEqual(len(self.base.orientacoes), 1)

    def test_cadastrar_invalido(self):
        with self.assertRaises(ValueError):
            self.base.cadastrar(dados(1, chaves=["a", "b"]))   # menos de 3 palavras-chave
        faltando = dados(2)
        del faltando["fonte"]
        with self.assertRaises(ValueError):
            self.base.cadastrar(faltando)

    def test_consultar_inexistente_e_lista_vazia(self):
        self.assertIsNone(self.base.consultar(99)[0])
        self.assertEqual(self.base.categorias(), [])
        self.assertEqual(self.base.buscar("qualquer coisa"), [])

    def test_atualizar_valido_e_invalido(self):
        self.base.cadastrar(dados(1))
        self.base.atualizar(1, "titulo", "Novo titulo")
        self.assertEqual(self.base.consultar(1)[0].titulo, "Novo titulo")
        with self.assertRaises(ValueError):
            self.base.atualizar(1, "palavras_chave", ["so", "duas"])
        self.assertEqual(len(self.base.consultar(1)[0].palavras_chave), 3)   # não mudou
        with self.assertRaises(LookupError):
            self.base.atualizar(99, "titulo", "x")

    def test_excluir(self):
        self.base.cadastrar(dados(1))
        self.base.cadastrar(dados(2))
        self.base.excluir(1)
        self.assertEqual([o.id for o in self.base.orientacoes], [2])
        with self.assertRaises(LookupError):
            self.base.excluir(1)

    def test_carregar_arquivo_ausente(self):
        self.assertFalse(self.base.carregar())
        self.assertTrue(self.base.avisos)

    def test_carregar_arquivo_corrompido(self):
        with open(self.caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write("{isto nao e json")
        self.assertFalse(self.base.carregar())
        self.assertEqual(len(self.base.orientacoes), 0)
        self.assertTrue(os.path.exists(self.caminho + ".corrompido"))

    def test_salvar_e_carregar(self):
        self.base.cadastrar(dados(1, "Cat A"))
        self.base.cadastrar(dados(2, "Cat B"))
        self.assertTrue(self.base.salvar())
        outra = BaseConhecimento(self.caminho)
        self.assertTrue(outra.carregar())
        self.assertEqual([o.id for o in outra.orientacoes], [1, 2])
        self.assertEqual(outra.categorias(), ["Cat A", "Cat B"])

    def test_ordenar_nao_altera_a_lista_original(self):
        self.base.cadastrar(dados(3, titulo="C"))
        self.base.cadastrar(dados(1, titulo="A"))
        self.base.cadastrar(dados(2, titulo="B"))
        ordenada = self.base.ordenar("id")
        self.assertEqual([o.id for o in ordenada], [1, 2, 3])
        self.assertEqual([o.id for o in self.base.orientacoes], [3, 1, 2])
        with self.assertRaises(ValueError):
            self.base.ordenar("inexistente")


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pasta, True)
        base = BaseConhecimento(os.path.join(self.pasta, "base.json"))
        self.assistente = Assistente("Teste", base)

    def test_indicadores_sem_atendimentos(self):
        ind = self.assistente.indicadores()
        self.assertEqual(ind["total"], 0)
        self.assertIsNone(ind["tempo_medio"])
        self.assertEqual(ind["sem_solucao"], [])

    def test_indicadores_com_atendimentos(self):
        self.assistente.registrar("pergunta", "duvida a", 1, True, True, 1, 4.0)
        self.assistente.registrar("pergunta", "xyz", None, False, False, 3, 10.0)
        self.assistente.registrar_nota(4)
        self.assistente.registrar_nota(5)
        ind = self.assistente.indicadores()
        self.assertEqual(ind["resposta_encontrada_pct"], 50.0)
        self.assertEqual(ind["acerto_pct"], 50.0)
        self.assertEqual(ind["tempo_medio"], 4.0)
        self.assertEqual(ind["tentativas_media"], 2.0)
        self.assertEqual(ind["facilidade_media"], 4.5)
        self.assertEqual(ind["sem_solucao"], ["xyz"])

    def test_exportar_csv(self):
        self.assistente.registrar("categoria", "titulo", 2, True, True, 1, 2.5)
        self.assertTrue(self.assistente.exportar_csv())
        with open(self.assistente.caminho_csv, newline="", encoding="utf-8-sig") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["origem"], "categoria")

    def test_historico_persiste(self):
        self.assistente.registrar("pergunta", "p", 1, True, True, 1, 1.0)
        novo = Assistente("Teste", self.assistente.base)
        self.assertEqual(len(novo.historico), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)