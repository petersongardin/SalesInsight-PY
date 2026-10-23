# Guia de estudo — SalesInsight PY

Para estudar com calma e para apresentar com domínio (não só decorar a
resposta da prova). Ordem: leia **o que é**, leia **por que foi usado aqui**,
abra a função indicada em `salesinsight.py`, rode, depois leia **como
explicar em voz alta** e responda a pergunta de prova (resposta no fim).

Rodar tudo: `python salesinsight.py` — depois abra `outputs/graficos/`.

---

## RF01 — Gerar o dataset · `gerar_dataset_vendas`

**O que é:** o dataset não veio de um arquivo externo — é **sintético**,
criado por código. Uma lista de dicionários (`dados = []`, depois
`dados.append({...})`) onde cada dicionário é um registro de venda; ao final,
`pd.DataFrame(dados)` transforma essa lista em uma tabela: cada chave do
dicionário vira uma coluna, cada dicionário vira uma linha.

**Por que assim:** o enunciado permitia gerar o próprio dado em vez de usar
um arquivo pronto. Gerar por código (em vez de digitar um CSV à mão) é o que
dá controle total sobre o experimento: decido exatamente quantos registros,
quais produtos existem, e consigo "sujar" propositalmente ~3% das datas
(`if random.random() < 0.03: data_txt = "DATA INVALIDA"`) para ter o que
limpar no RF03. Sem essa sujeira proposital, a etapa de limpeza não teria
nada para fazer.

**Reprodutibilidade:** `random.seed(seed)` e `np.random.seed(seed)` fixam o
"estado interno" do gerador de números pseudoaleatórios. O computador não
sorteia de verdade — ele segue uma sequência determinística a partir da
seed. Com `seed=42`, qualquer pessoa que rodar este código, em qualquer
máquina, gera exatamente os mesmos 200 registros. Isso importa porque sem
isso o relatório de limpeza (6 removidas, 194 finais) mudaria a cada execução
e ninguém conseguiria reproduzir um bug reportado por outra pessoa.

**`strftime`:** `data.strftime("%Y-%m-%d")` converte um objeto `datetime`
(interno, numérico) em texto formatado. Por isso a coluna `data_venda` sai
do CSV como string, não como data — o RF03 é quem converte de volta.

**Como explicar no vídeo:** "Gerei o dataset no próprio código com uma seed
fixa, para ser 100% reprodutível, e sujei de propósito 3% das datas para ter
algo real para limpar depois."

❓ **P1:** por que a seed importa?

---

## RF02 — Inspecionar · `inspecionar_dados`

**O que é:** uma leitura **estrutural** dos dados, sem interpretar
estatística ainda. `.shape` dá (linhas, colunas); `.columns` lista os nomes;
`.dtypes` mostra o tipo de cada coluna (`int64`, `float64`, `object`);
`.isnull().sum()` conta células vazias por coluna; `.head()` mostra as 5
primeiras linhas.

**Por que assim:** antes de limpar ou calcular qualquer métrica, preciso
saber o que tenho: quantas linhas sobreviveram à geração, se os tipos vieram
como eu esperava, e se existe sujeira visível. É o equivalente a abrir uma
planilha e olhar antes de aplicar fórmula.

**A pegadinha do `isnull()`:** `isnull()` só detecta células **vazias**
(`NaN`/`None`). A string `"DATA INVALIDA"` é texto **preenchido** — não é
nula — então `isnull()` conta 0 nessa coluna mesmo havendo datas inválidas.
Ela só vira nula (`NaT`) depois que o RF03 tenta convertê-la para data de
verdade e falha.

**Como explicar no vídeo:** "Antes de tratar qualquer coisa, inspecionei a
estrutura: shape, tipos de coluna e nulos. Reparei que `isnull()` não pega
a sujeira textual — isso só aparece depois da conversão de data no RF03."

❓ **P2:** por que `isnull()` dá 0 em `data_venda` mesmo havendo datas inválidas?

---

## RF03 — Limpar · `tratar_dados`

**O que é:** a etapa de limpeza, que roda **antes** de qualquer coluna
derivada, agregação ou gráfico. `.str.strip()` remove espaços nas pontas do
texto. `pd.to_datetime(df["data_venda"], errors="coerce")` tenta converter
cada valor de texto para data real; o que não converte (como
`"DATA INVALIDA"`) vira `NaT` (Not a Time, o "nulo" de datas) em vez de
quebrar o programa com um erro. `dropna(subset=["data_venda"])` remove só as
linhas onde `data_venda` é `NaT`. Por fim, `.astype(int)` e `.astype(float)`
garantem os tipos numéricos corretos, e `df.copy()` no início evita alterar
o DataFrame original que ainda está guardado em `self.df_bruto`.

**Por que remover, e não imputar:** a decisão registrada no projeto foi
**remover** as linhas com data inválida, não preencher com uma data
qualquer (imputação). Sem uma data válida, não é possível atribuir aquela
venda a um mês, trimestre ou ano — qualquer valor que eu inventasse ali
distorceria as métricas por período de forma silenciosa. Como são apenas
6 de 200 registros (3%), a perda de informação é pequena e totalmente
registrada no relatório de limpeza — é uma decisão transparente, não dado
escondido. (Imputação de nulos é conteúdo das semanas 09–11, fora do escopo
deste módulo.)

**Por que a limpeza vem primeiro:** se as colunas derivadas (RF04) ou as
agregações (RF05) rodassem antes da limpeza, elas processariam o texto
`"DATA INVALIDA"` como se fosse uma data, gerando `NaN` propagado ou erro em
cascata nas etapas seguintes. Limpar primeiro garante que nenhuma etapa
posterior trabalha com lixo.

**Resultado real:** entraram 200, removidas 6, finais 194. "Colunas com
tipo convertido: 0" não é bug — os tipos numéricos (`quantidade`,
`preco_unitario`) já vinham corretos desde a geração; só a data precisava de
conversão, e ela é tratada separadamente no relatório.

**Estrutura de retorno:** a função devolve uma **tupla** `(df_limpo,
relatorio)` — dois valores em uma única instrução `return`. `relatorio` é
um **dicionário** com as chaves `registros_iniciais`, `datas_invalidas_removidas`,
`colunas_com_tipo_convertido`, `registros_finais`.

**Como explicar no vídeo:** "Removi as datas inválidas em vez de mantê-las
porque sem data não consigo atribuir a venda a um mês ou trimestre; manter
distorceria as métricas por período. Eram 6 de 200 registros (3%), e a
perda aparece no relatório de limpeza — não escondi nada."

❓ **P3:** por que a limpeza vem antes das agregações e gráficos?

---

## RF04 — Colunas derivadas · `criar_colunas_derivadas`

**O que é:** colunas que não vêm do dado bruto, mas são calculadas a partir
dele. `receita_total = quantidade * preco_unitario` é **vetorizado** — a
multiplicação roda na coluna inteira de uma vez, sem precisar de um `for`
percorrendo linha a linha (o Pandas/NumPy fazem isso internamente, em C,
muito mais rápido que um loop Python). `.dt.month`, `.dt.quarter`, `.dt.year`
são *accessors* de data que extraem partes de uma coluna `datetime64`.

**Por que `.map()` em vez de `%B`:** `data.strftime("%B")` devolveria o nome
do mês em inglês (ou dependente do idioma configurado no sistema/Colab) —
não é confiável. Usar `.map(MESES_PT)`, um dicionário `{1: "Janeiro", 2:
"Fevereiro", ...}`, garante nome em português sempre, em qualquer máquina.

**`np.select`:** é um "if/elif/else vetorizado". Em vez de testar condição
por condição com um loop, passo uma lista de condições booleanas
(`condicoes`) e uma lista de resultados correspondentes (`faixas`); o NumPy
aplica a primeira condição verdadeira de cada linha. O operador `&` (e
lógico, bit a bit) combina duas comparações — é diferente do `and` comum do
Python porque opera em arrays inteiros, não em um único booleano, por isso
cada comparação precisa ir entre parênteses:
`(df["receita_total"] >= 500) & (df["receita_total"] < 5000)`. O `default`
é o valor usado quando **nenhuma** condição é verdadeira (rede de segurança).

**Como explicar no vídeo:** "Derivei receita, mês, trimestre e ano a partir
da data e do preço, tudo vetorizado — sem loop manual. Para o nome do mês em
português usei um dicionário, porque `strftime` depende do idioma do
sistema. E para classificar a faixa de valor usei `np.select`, que é como
um if/elif/else que roda na coluna inteira de uma vez."

❓ **P4:** o que faz o `default` do `np.select`?

---

## RF05 — Métricas agregadas · `calcular_metricas`

**O que é:** `df.groupby("mes")` agrupa todas as linhas que têm o mesmo mês
em um "balde"; `.agg(receita_total=("receita_total", "sum"), ...)` calcula,
dentro de cada balde, a soma/contagem/média pedida, e nomeia o resultado.
`.sort_values(ascending=False).head(5)` ordena do maior para o menor e
pega os 5 primeiros (top produtos). `.reset_index()` transforma o índice do
agrupamento de volta em coluna normal, para a tabela ficar "plana" e fácil
de exportar/plotar.

**Por que `agg` com nomes:** usar `.agg(nome_saida=("coluna_origem",
"funcao"))` (named aggregation) deixa explícito, na própria chamada, qual
nome cada métrica vai ter — mais legível do que `.agg({"col": "sum"})`
seguido de um `rename` separado.

**Ticket médio:** é a média (`"mean"`) da receita por venda dentro do grupo
(região, por exemplo) — não confundir com a soma. Soma dá o total movimentado
pela região; média dá o "tamanho típico" de uma venda naquela região.

**Estrutura de retorno:** a função devolve um **dicionário de DataFrames**
— `{"por_mes": df1, "por_trimestre": df2, "top_produtos": df3, ...}` — assim
cada métrica fica acessível pelo nome (`metricas["por_mes"]`) em vez de
precisar de 5 variáveis soltas.

**Como explicar no vídeo:** "Agrupei por mês, trimestre, produto, categoria e
região com `groupby` + `agg`, cada métrica com o agregador certo: soma para
receita total, contagem para número de vendas, média para ticket médio."

❓ **P5:** diferença entre `sum` e `count` no `.agg`?

---

## RF06 — Segmentação de clientes · `segmentar_clientes`

**O que é:** `groupby("cliente")["receita_total"].sum()` soma tudo que cada
cliente gastou, virando uma linha por cliente com o total. Em seguida,
`.apply(lambda v: "Bronze" if v < 5000 else ("Prata" if v <= 15000 else
"Ouro"))` roda essa regra para **cada valor** da coluna `total_gasto`, uma
linha por vez, e devolve o segmento correspondente.

**O que é um `lambda`:** uma função anônima de uma linha, sem nome e sem
`def`. `lambda v: "Bronze" if v < 5000 else (...)` é exatamente equivalente a
escrever uma função normal com `def segmento(v): ...` — a diferença é só
sintática: o lambda é útil quando a função é curta e só vai ser usada naquele
ponto específico, sem precisar de um nome reutilizável.

**Por que os limites do enunciado geram "maioria em Ouro":** com os cortes
dados (Bronze < R$ 5.000; Prata até R$ 15.000; Ouro > R$ 15.000), 35 dos 49
clientes caem em Ouro. Isso é esperado matematicamente: a receita total do
dataset (R$ 1.380.210,31) dividida por 49 clientes já dá uma média de gasto
bem acima de R$ 15.000, então os limites do enunciado — pensados talvez para
outra escala de dados — empurram a maioria para a faixa mais alta. Isso foi
mantido porque o enunciado fixou esses valores; não é um bug do código, é uma
limitação conhecida e documentada.

**Como explicar no vídeo:** "Somei o gasto por cliente e usei um lambda para
classificar em Bronze, Prata ou Ouro pelos limites do enunciado. Com a
escala do meu dataset, a maioria cai em Ouro — documentei isso como
limitação conhecida, não escondi."

❓ **P6:** reescreva o lambda como função normal (`def`).

---

## RF07 — Gráficos · `grafico_*` e `_salvar`

**O que é:** `fig, ax = plt.subplots(figsize=...)` cria dois objetos: `fig`
é a "folha de papel" inteira (a figura), `ax` é o sistema de eixos — o
gráfico propriamente dito — desenhado dentro dela. Separar os dois é o que
permite, no painel (RF07 painel), ter 4 gráficos (`axes` 2×2) dentro de uma
única figura.

**Itens obrigatórios em cada gráfico:** título (`set_title`), rótulos dos
eixos (`set_xlabel`/`set_ylabel`), legenda quando há cores distintas
(`legend()`), tamanho definido (`figsize`), paleta de cores escolhida
conscientemente, `tight_layout()` (evita textos cortados nas bordas),
`savefig(dpi>=100)` (resolução suficiente para leitura) e `plt.close()`
depois de salvar (libera memória — sem isso, gerar muitos gráficos em
sequência acumula figuras abertas).

**Painel 2×2:** `plt.subplots(2, 2)` devolve uma matriz `axes` de 2 linhas
por 2 colunas. `axes[0, 0]` é a posição linha 0, coluna 0 (canto superior
esquerdo); `axes[1, 0]` é linha 1, coluna 0 (canto inferior esquerdo).
`fig.suptitle(...)` define um título único para a figura toda, por cima dos
4 subgráficos.

**Seaborn:** ao usar `palette` num gráfico seaborn (`barplot`, `scatterplot`)
é necessário também passar `hue=...` (a coluna que define a cor); quando o
`hue` é só decorativo (não precisa de legenda separada, como no gráfico de
barras onde cada barra já tem o rótulo no eixo), usa-se `legend=False` para
não duplicar informação e evitar o aviso de depreciação do Seaborn.

**`matplotlib.use("Agg")`:** define o backend (motor de renderização) do
Matplotlib como "Agg", que desenha diretamente em arquivo (PNG) sem tentar
abrir uma janela gráfica interativa. Essencial para rodar em servidor, CI ou
Colab, onde não existe tela.

**Como explicar no vídeo:** "Cada gráfico segue o mesmo padrão: título,
eixos nomeados, legenda quando preciso, `tight_layout` e salvo em PNG com
boa resolução. No painel final combino os 4 numa grade 2×2 — `axes[0,0]` é a
receita por mês, `axes[1,0]` é a dispersão quantidade x receita."

❓ **P7:** o que `axes[1, 0]` seleciona?

---

## RF08 — Função de ordem superior · `processar_coluna`

**O que é:** uma função de ordem superior (higher-order function) é
qualquer função que recebe **outra função como argumento** e/ou devolve uma
função. `processar_coluna(df, coluna, funcao_transformacao, nome_saida)`
recebe `funcao_transformacao` como parâmetro e aplica ela a cada valor da
coluna via `.apply()`, sem saber de antemão qual transformação vai ser
usada — isso é decidido por quem chama a função.

**Os 3 usos no projeto:** (1) o segmento de cliente, dentro de
`segmentar_clientes`; (2) `receita_em_milhares` — `lambda x: round(x / 1000,
2)` — dentro de `transformar()` da classe; (3) `perfil_volume` —
`lambda q: "Alto Volume" if q > 5 else "Baixo Volume"` — também em
`transformar()`.

**Por que isso é útil:** sem `processar_coluna`, cada transformação
precisaria de uma função separada e repetida (`def transforma_receita(df):
...`, `def transforma_volume(df): ...`), cada uma reimplementando a mesma
lógica de "aplicar algo a uma coluna e salvar em outra". Com a função de
ordem superior, a lógica de "como aplicar" é escrita uma vez só; muda apenas
o "o quê aplicar" (o lambda passado).

**Como explicar no vídeo:** "`processar_coluna` recebe a transformação como
parâmetro — por isso é de ordem superior. Uso ela três vezes com lambdas
diferentes, sem repetir a lógica de aplicar a coluna."

❓ **P8:** por que `processar_coluna` é "de ordem superior"?

---

## RF09 — Exportação CSV e JSON · `exportar_resultados`

**O que é:** `.to_csv(index=False, encoding="utf-8-sig")` grava a tabela em
CSV sem uma coluna extra de índice numérico, e com encoding `utf-8-sig`
(UTF-8 com marca BOM) para que o Excel abra os acentos corretamente — sem o
BOM, o Excel às vezes interpreta UTF-8 comum como Latin-1 e corrompe
caracteres acentuados. `json.dump(obj, f, indent=4, ensure_ascii=False)`
escreve um dicionário Python como JSON formatado, preservando acentos
(`ensure_ascii=False`).

**Por que converter para `float()` antes do JSON:** o formato JSON só aceita
tipos simples (número, texto, booleano, lista, objeto) — não aceita tipos
específicos do NumPy/Pandas como `numpy.int64` ou `numpy.float64`, mesmo que
pareçam números comuns. Por isso `{k: round(float(v), 2) for k, v in
estatisticas.items()}` converte cada valor explicitamente antes de tentar
serializar, evitando um `TypeError` na gravação.

**Por que reler o JSON depois de escrever:** `json.load(f)` depois do
`json.dump` não é redundante — é a prova de que o arquivo foi gravado
corretamente e é um JSON válido e legível. Se o arquivo tivesse ficado
corrompido ou mal formatado, essa releitura falharia imediatamente, em vez
de o erro aparecer só quando outra parte do sistema tentasse ler o arquivo
depois.

**Como explicar no vídeo:** "Exporto CSV com encoding compatível com Excel e
JSON com os floats convertidos explicitamente, porque tipos do NumPy não são
serializáveis direto. E releio o JSON na hora, como prova de que a gravação
funcionou."

❓ **P9:** por que reler o JSON depois de gravar?

---

## RF10 — Orquestração · `main` e `AnalisadorDeVendas`

**O que é:** a classe `AnalisadorDeVendas` guarda o **estado** do fluxo —
`self.df_bruto`, `self.df`, `self.relatorio`, `self.metricas`,
`self.clientes` — entre uma etapa e outra. Cada método (`carregar`,
`transformar`, `analisar`, `visualizar`, `resumo`) é uma etapa do pipeline
que lê e atualiza esse estado interno. Isso evita passar 5 variáveis soltas
de função em função — o objeto carrega tudo junto.

**Ordem de execução (fixa e intencional):** carregar → inspecionar →
transformar (limpeza **antes** das derivadas, dentro do próprio
`transformar()`) → analisar (métricas + segmentação) → visualizar (os 4
gráficos) → resumo (estatísticas gerais + exportação). Inverter essa ordem
quebraria etapas posteriores — por exemplo, calcular métricas antes de
limpar processaria datas inválidas como se fossem válidas.

**`if __name__ == "__main__":`:** essa linha verifica se o arquivo está
sendo executado diretamente (`python salesinsight.py`) ou importado por
outro arquivo (`import salesinsight`). Quando importado, a variável especial
`__name__` não vale `"__main__"`, então `main()` **não roda automaticamente**
— quem importa o módulo só ganha acesso às funções e classes, sem disparar
o pipeline inteiro de novo. Isso é o padrão usado para tornar um arquivo
Python reaproveitável como biblioteca e executável como script ao mesmo
tempo.

**Como explicar no vídeo:** "A classe `AnalisadorDeVendas` guarda o estado
entre as etapas, e `main()` só roda quando o arquivo é executado direto —
isso é o que o `if __name__ == '__main__'` garante, e é o que permite
reimportar o módulo em outro projeto sem disparar tudo de novo."

❓ **P10:** o que acontece com `main()` se outro arquivo fizer `import salesinsight`?

---

## Git (Semana 04)

**O que é:** controle de versão — cada mudança fica registrada como um
"commit" (uma foto do projeto naquele momento, com uma mensagem explicando o
que mudou). Branches são linhas paralelas de desenvolvimento que depois se
juntam (merge).

**Convenção usada neste projeto:** `main` é a versão estável/publicável;
`develop` é onde o trabalho de diferentes frentes se integra antes de ir
para `main`; `feat/...` é uma branch de funcionalidade específica (aqui,
`feat/pipeline-dados`, que concentrou RF01–RF09); `docs/...` é uma branch só
de documentação (`docs/readme`). As mensagens seguem *conventional commits*:
prefixo `feat:` para funcionalidade nova, `fix:` para correção, `docs:` para
documentação, `merge:` para junções de branch.

**Por que branches separadas em vez de tudo direto na `main`:** isolar o
trabalho em progresso, poder revisar/testar antes de integrar, e ter um
histórico que mostra a evolução por assunto (dado, docs, etc.) — é a prática
pedida pelo enunciado (mínimo 5 commits, individual).

**Como explicar no vídeo:** "Organizei o trabalho em branches por
funcionalidade e documentação, com commits no padrão conventional commits, e
integrei tudo via merge na `develop` e depois na `main`."

---

## Respostas (conferência rápida)

1. Mesma seed = mesmos dados em qualquer máquina (reprodutível, depurável).
2. Está preenchida com texto; `isnull` só vê vazios. Vira `NaT` só após `to_datetime(coerce)`.
3. Para nenhuma etapa usar dados inválidos; mês/trimestre dependem de data válida.
4. Valor usado quando nenhuma condição é verdadeira ("Nao Classificado").
5. `sum` soma os valores; `count` conta quantas linhas há no grupo.
6. `def segmento(v): if v < 5000: return "Bronze" / elif v <= 15000: return "Prata" / else: return "Ouro"`.
7. Linha 1, coluna 0 (segunda linha, primeira coluna): o gráfico de dispersão.
8. Porque recebe outra função (`lambda`) como parâmetro.
9. Para comprovar que o arquivo foi gravado e é válido.
10. Nada: o `if __name__` impede a execução; só roda ao executar o arquivo direto.

## Roteiro de explicação para o vídeo (decisão técnica)

"Removi as datas inválidas em vez de mantê-las porque sem data não consigo
atribuir a venda a um mês ou trimestre; manter distorceria as métricas por
período. Eram 6 de 200 registros (3%), e a perda aparece no relatório de
limpeza."
