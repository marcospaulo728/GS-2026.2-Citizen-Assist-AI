# Citizen Assist AI — Assistente Digital de Orientação ao Cidadão

Projeto integrado da Global Solution 2026.2 (CitizenTech) para as disciplinas
**Pensamento Computacional e Automação com Python (PCP)** e **Data Structures and Algorithms (DSA)**.

## Integrantes • 1CCR
| Nome | RM |
|---|---|
| Marcos Paulo Sampaio | 573987 |
| Gabriela Angel Silva | 570808 |
| Izabelly Menezes | 570673 | 

Izabelly Menezes ---> Apenas na disciplina de DSA!

## Público e problema
**Público:** jovens no primeiro emprego.
**Problema:** a informação sobre carteira de trabalho digital, CPF, gov.br, título de eleitor e
alistamento está espalhada, em linguagem técnica e misturada com páginas que parecem oficiais e não são.
O assistente responde com base em uma base verificada, mostra fonte, data de verificação e aviso de
limitação, e não coleta dados pessoais.

## ODS relacionados
- ODS 8 (Trabalho decente)
- ODS 16 (Instituições eficazes e acesso à informação)
- ODS 10 (Redução das desigualdades)

## Como executar
Requisitos: Python 3.8+ (sem bibliotecas externas).
```
python main.py          # executa o assistente
python testes.py        # executa os testes automatizados
```

## Estrutura
```
citizen-assist-ai/
├── main.py                 # menu e ponto de entrada
├── orientacao.py           # classe Orientacao
├── base_conhecimento.py    # classe BaseConhecimento (lista encadeada, pontuação, CRUD)
├── assistente.py           # classe Assistente (atendimento, histórico, indicadores, CSV)
├── lista_encadeada.py      # No e ListaEncadeada (DSA)
├── algoritmos.py           # buscas sequenciais (DSA)
├── gestao.py               # telas de CRUD, pesquisa, ordenação e análise
├── utilitarios.py          # normalizar(), validações, leitura de JSON
├── testes.py               # testes automatizados
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    ├── avaliacoes.json
    └── atendimentos.csv
```

## Classes (PCP)
- `Orientacao`: um registro do JSON. Método `exibir()`.
- `BaseConhecimento`: `caminho`, `orientacoes`; `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`.
- `Assistente`: `nome`, `base`, `historico`; `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`.
- Composição: `Assistente → BaseConhecimento → ListaEncadeada de Orientacao`.

## Regra de pontuação
- +3 pontos por palavra-chave da orientação que aparece na pergunta.
- +1 ponto por palavra da pergunta (4 letras ou mais) que aparece no título.
- Confiança ALTA com 6 pontos ou mais; MÉDIA com 3 a 5; abaixo de 3: "não encontrei".
- Pergunta, palavras-chave e título são normalizados (minúsculas, sem acentos, sem pontuação).
- `buscar()` devolve uma lista de tuplas `(pontos, orientacao)` em ordem decrescente.
  O desempate é estável (a orientação que aparece antes na lista fica na frente).
- Os pesos e limites são os do enunciado, sem ajustes.

## Integração PCP + DSA
- A base é uma **lista encadeada própria** (`ListaEncadeada`, com `No.proximo`) e é a mesma estrutura
  usada na busca do assistente e no CRUD.
- Inserção no fim O(1) (ponteiro para a cauda), remoção O(n), busca sequencial O(n).
- Ordenação: **Merge Sort** sobre os nós da lista, O(n log n), estável. Também ordena as tuplas
  `(pontos, orientacao)` da busca.
- Toda alteração do CRUD é gravada no mesmo `base_conhecimento.json` lido pelo assistente.

## Análise Big-O
| Operação | Tempo |
|---|---|
| Inserir no início / no fim | O(1) |
| Cadastro (inclui verificar ID duplicado) | O(n) |
| Busca por ID | O(1) melhor, O(n) pior e médio |
| Pesquisa por texto | O(n·L) |
| Remoção | O(n) |
| Merge Sort | O(n log n) |

Justificativas completas na documentação técnica. Busca binária não é usada porque a lista
encadeada não tem acesso por índice em O(1).

## Regras de atendimento
Nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e
não é registrada. Toda resposta mostra fonte, data de verificação e o aviso de que o assistente não é
canal oficial. JSON ausente ou corrompido não trava o programa.

## Indicadores
Resposta encontrada (%), taxa de acerto: ajudou (%) (sobre o total de atendimentos), tempo médio para
encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução.

## Fontes consultadas (10/11/2026)
- https://www.gov.br/receitafederal
- https://www.gov.br/governodigital
- https://www.gov.br/trabalho-e-emprego
- https://www.caixa.gov.br
- https://www.gov.br/inss
- https://www.tse.jus.br
- https://www.gov.br/defesa
- https://www.gov.br

## Teste com usuários
- Pessoas externas à equipe: 3
- Atendimentos totais: 14
- Resposta encontrada: 64.3%  | Taxa de acerto: 64.3%
- Tempo médio para encontrar: 21.7 s | Tentativas por atendimento: 1.2 | Facilidade (1–5): 4
- Melhoria feita a partir do teste: Inserção de novas palavras-chave

## Limitações
- Busca por regras: não entende sinônimos, erros de digitação nem contexto.
- A base cobre poucos temas e precisa de revisão periódica das fontes.
- A medição de tempo inclui o tempo de leitura e digitação da pessoa.
- Registros inválidos no JSON são ignorados ao carregar e removidos na próxima gravação.

## Vídeo técnico
https://youtu.be/lX-ua0KCt4w
