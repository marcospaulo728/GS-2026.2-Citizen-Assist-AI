"""Classe Orientacao: um registro da base de conhecimento."""
from utilitarios import normalizar, data_valida

CAMPOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em")
CAMPOS_TEXTO = ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em")
PENDENTE = "PENDENTE"


class Orientacao:
    AVISO = "este assistente NÃO é um canal oficial."

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    # ------------------------------------------------------------ validação
    @staticmethod
    def validar_dados(dados):
        """Levanta ValueError se o dicionário não for um registro válido."""
        if not isinstance(dados, dict):
            raise ValueError("o registro não é um dicionário")
        ausentes = [campo for campo in CAMPOS if campo not in dados]
        if ausentes:
            raise ValueError("campos ausentes: " + ", ".join(ausentes))
        id_ = dados["id"]
        if not isinstance(id_, int) or isinstance(id_, bool) or id_ <= 0:
            raise ValueError("o id deve ser um inteiro positivo")
        for campo in CAMPOS_TEXTO:
            if not isinstance(dados[campo], str) or not dados[campo].strip():
                raise ValueError(f"o campo '{campo}' deve ser um texto não vazio")
        chaves = dados["palavras_chave"]
        if (not isinstance(chaves, list)
                or any(not isinstance(p, str) or not p.strip() for p in chaves)):
            raise ValueError("'palavras_chave' deve ser uma lista de textos não vazios")
        if len({normalizar(p) for p in chaves}) < 3:
            raise ValueError("são necessárias ao menos 3 palavras-chave diferentes")
        documentos = dados["documentos"]
        if (not isinstance(documentos, list)
                or any(not isinstance(d, str) for d in documentos)):
            raise ValueError("'documentos' deve ser uma lista de textos")
        if not dados["fonte"].strip().lower().startswith(("http://", "https://")):
            raise ValueError("a fonte deve ser um endereço que comece com http(s)://")
        verificado = dados["verificado_em"].strip()
        if verificado != PENDENTE and not data_valida(verificado):
            raise ValueError("'verificado_em' deve estar no formato AAAA-MM-DD "
                             f"(ou {PENDENTE})")

    @classmethod
    def de_dict(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON (validando)."""
        cls.validar_dados(dados)
        return cls(
            id=dados["id"],
            categoria=dados["categoria"].strip(),
            titulo=dados["titulo"].strip(),
            palavras_chave=[p.strip() for p in dados["palavras_chave"]],
            resposta=dados["resposta"].strip(),
            documentos=[d.strip() for d in dados["documentos"] if d.strip()],
            onde=dados["onde"].strip(),
            fonte=dados["fonte"].strip(),
            verificado_em=dados["verificado_em"].strip(),
        )

    def para_dict(self):
        return {
            "id": self.id,
            "categoria": self.categoria,
            "titulo": self.titulo,
            "palavras_chave": list(self.palavras_chave),
            "resposta": self.resposta,
            "documentos": list(self.documentos),
            "onde": self.onde,
            "fonte": self.fonte,
            "verificado_em": self.verificado_em,
        }

    def copiar_de(self, outra):
        """Copia os campos de outra Orientacao (usado na atualização in place)."""
        for campo in CAMPOS:
            setattr(self, campo, getattr(outra, campo))

    # ------------------------------------------------------------- exibição
    def texto_verificacao(self):
        if self.verificado_em == PENDENTE:
            return "verificação pendente"
        return f"verificado em {self.verificado_em}"

    def exibir(self):
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: nenhum informado.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} ({self.texto_verificacao()})")
        print(f"Aviso: {self.AVISO}")