# SalesInsight PY

## Sobre o projeto
Análise e visualização de dados de vendas desenvolvida em Python. O projeto
gera (ou carrega), limpa, transforma, agrega e visualiza um dataset de vendas,
produzindo métricas por período, produto, categoria e região, além de uma
segmentação simples de clientes por faixa de gasto (Bronze, Prata, Ouro).

Mini-Projeto Avaliativo M1.1 — Desenvolvedor(a) em IA para Análise Preditiva, Módulo 01.

## O que o projeto analisa
- Receita total e volume de vendas por mês e por trimestre
- Top produtos e categorias por receita
- Desempenho por região (receita e ticket médio)
- Segmentação de clientes por nível de gasto (Bronze, Prata, Ouro)
- Relação entre quantidade vendida e receita por transação
- Exportação de relatórios em CSV e JSON e de gráficos em PNG

## Conceitos aplicados (Módulo 01 — Semanas 01 a 07)
- **Lógica de programação:** variáveis, tipos (`int`, `float`, `str`, `bool`, `list`, `dict`), operadores, `if/elif/else`, `for`
- **Estruturas de dados:** lista de dicionários (dataset), dicionário de métricas, dicionário de relatório de limpeza
- **Funções:** parâmetros, retorno, docstring, `lambda` (3 usos), função de ordem superior (`processar_coluna`)
- **Arquivos:** leitura/escrita de CSV (`read_csv`, `to_csv`) e JSON (`json.dump`, `json.load`)
- **datetime:** geração de datas, `pd.to_datetime(errors="coerce")`, `.dt.month/.quarter/.year`
- **Pandas:** DataFrames, filtros, `groupby` + `agg`, `sort_values`, `value_counts`, `apply`
- **NumPy:** operações vetorizadas e `np.select`
- **Matplotlib e Seaborn:** linha, barra, dispersão, subplots 2×2, customização e exportação PNG
- **Orientação a objetos básica:** classe `AnalisadorDeVendas`
- **Git e GitHub:** branches por funcionalidade e commits no padrão *conventional commits*

## Como executar

### Google Colab
1. Faça upload de `salesinsight.py` para o Colab.
2. Execute: `!python salesinsight.py` (o `vendas.csv` é gerado automaticamente).

### Localmente (VS Code / terminal)
1. Instale o Python 3.10+.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute:
   ```
   python salesinsight.py
   ```

## Estrutura do projeto
```
salesinsight-py/
|-- salesinsight.py         # fluxo principal
|-- vendas.csv              # dataset (gerado pelo código)
|-- requirements.txt
|-- README.md
|-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/
        |-- receita_por_mes.png
        |-- top_produtos.png
        |-- quantidade_vs_receita.png
        |-- painel_resumo.png
```

## Decisões técnicas
- **Datas inválidas são removidas, não mantidas.** Sem data não é possível
  atribuir a venda a mês/trimestre, então mantê-la distorceria as métricas por
  período. Como são ~3% dos registros (6 de 200), a perda é pequena e é
  registrada no relatório de limpeza. Não usei imputação (conteúdo das semanas 09–11).
- **Limpeza antes de tudo:** `tratar_dados` roda antes das colunas derivadas,
  das agregações e dos gráficos, para que nenhuma etapa trabalhe com dados inválidos.
- **Nomes de mês por dicionário** (`MESES_PT`), porque `strftime("%B")` retorna inglês no Colab.
- **`seed=42`** no gerador, para o dataset ser idêntico em qualquer máquina.

## Limitações conhecidas
- O gerador só "suja" a coluna de data; por isso o relatório mostra 0 colunas com tipo convertido (os tipos numéricos já vêm corretos do CSV).
- Com os limites do enunciado (Bronze < R$ 5.000; Ouro > R$ 15.000), a maioria dos clientes cai em Ouro (35 de 49).

## Ferramentas utilizadas
- Python 3.10+
- Bibliotecas: pandas, numpy, matplotlib, seaborn, json, datetime, os, random
- VS Code / Google Colab
- Git e GitHub

## Vídeo de demonstração
[inserir o link do Google Drive ou do YouTube aqui]
