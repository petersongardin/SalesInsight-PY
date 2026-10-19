# Guia de estudo — SalesInsight PY

Para estudar com calma. Ordem: leia o conceito, abra a função indicada em
`salesinsight.py`, rode, responda a pergunta de prova (resposta no fim).

Rodar tudo: `python salesinsight.py` — depois abra `outputs/graficos/`.

---

## RF01 — Gerar o dataset · `gerar_dataset_vendas`
- **Lista de dicionários → DataFrame:** cada `dict` é uma linha; as chaves viram colunas.
- **`seed`:** o computador só *simula* sorteio; com a mesma semente a sequência é idêntica → reprodutibilidade.
- **`for` + `if`:** o `for` cria 200 registros; o `if random.random() < 0.03` suja ~3% das datas.
- **`strftime`:** data → texto (`"2025-05-21"`). Por isso a coluna sai do CSV como texto.
- ❓ P1: por que a seed importa?

## RF02 — Inspecionar · `inspecionar_dados`
- `.shape` (linhas, colunas), `.columns`, `.dtypes`, `.isnull().sum()`, `.head()`: descrevem a **estrutura**, não interpretam estatística.
- `isnull()` detecta só células **vazias**. `"DATA INVALIDA"` é texto preenchido → conta 0.
- ❓ P2: por que `isnull()` dá 0 em `data_venda` mesmo havendo datas inválidas?

## RF03 — Limpar · `tratar_dados`
- `.str.strip()` remove espaços das pontas do texto.
- `pd.to_datetime(..., errors="coerce")`: o que não converte vira `NaT` (data vazia) em vez de erro.
- `dropna(subset=[...])`: remove as linhas com `NaT`. **Decisão:** sem data não há mês/trimestre.
- `.astype(int)` / `.astype(float)`: garante os tipos. `df.copy()` evita alterar o original.
- Retorna **tupla** `(df_limpo, relatorio)`; o relatório é um **dicionário**.
- Resultado real: entraram 200, removidas 6, finais 194. Tipos convertidos: 0 (já vinham certos — é honesto, não é bug).
- ❓ P3: por que a limpeza vem antes das agregações e gráficos?

## RF04 — Colunas derivadas · `criar_colunas_derivadas`
- **Vetorizado:** `quantidade * preco_unitario` opera na coluna inteira, sem `for`.
- `.dt.month`, `.dt.quarter`, `.dt.year`: extraem partes da data.
- `.map(dicionario)`: troca 1→"Janeiro". Não use `%B` (sai em inglês no Colab).
- `np.select(condicoes, faixas, default=...)`: um "if/elif/else" vetorizado, com `&` (e) entre comparações e parênteses.
- ❓ P4: o que faz o `default` do `np.select`?

## RF05 — groupby · `calcular_metricas`
- `df.groupby("mes")` → agrupa; `.agg(nome=("coluna","sum"))` → calcula por grupo.
- `.sort_values(ascending=False).head(5)` → top 5; `.reset_index()` → volta a ser tabela.
- Ticket médio = média da receita por venda (`"mean"`).
- Retorna **dicionário de DataFrames**.
- ❓ P5: diferença entre `sum` e `count` no `.agg`?

## RF06 — Segmentação · `segmentar_clientes`
- `groupby("cliente")` soma o gasto; `.apply(lambda v: ...)` aplica uma regra a cada valor.
- **lambda** = função anônima de uma linha: `lambda v: "Bronze" if v < 5000 else ...`.
- `.value_counts()` conta quantos clientes há em cada segmento.
- ❓ P6: reescreva o lambda como função normal (`def`).

## RF07 — Gráficos · `grafico_*` e `_salvar`
- `fig, ax = plt.subplots(figsize=...)`: `fig` = a folha; `ax` = o gráfico dentro dela.
- Obrigatórios: título, rótulos dos eixos (`set_title/xlabel/ylabel`), legenda quando há cores, `figsize`, cores escolhidas, `tight_layout()`, `savefig(dpi>=100)`, `plt.close()`.
- Painel: `plt.subplots(2, 2)` devolve `axes` 2×2 → `axes[0, 0]` é o de cima à esquerda. `fig.suptitle` = título geral.
- Seaborn: `palette` exige `hue=...` e `legend=False` (evita aviso).
- `matplotlib.use("Agg")`: grava arquivo sem abrir janela.
- ❓ P7: o que `axes[1, 0]` seleciona?

## RF08 — Função de ordem superior · `processar_coluna`
- Recebe **uma função como argumento** (`funcao_transformacao`) e a aplica à coluna.
- Os 3 lambdas do projeto: segmento de cliente, `receita_em_milhares`, `perfil_volume`.
- ❓ P8: por que `processar_coluna` é "de ordem superior"?

## RF09 — CSV e JSON · `exportar_resultados`
- `.to_csv(index=False, encoding="utf-8-sig")`: sem coluna de índice; acentos ok no Excel.
- `json.dump(obj, f)` escreve; `json.load(f)` lê de volta (prova da gravação).
- JSON só aceita tipos simples → converter com `float(...)`.
- ❓ P9: por que reler o JSON depois de gravar?

## RF10 — main · `main` e `AnalisadorDeVendas`
- **Classe** guarda o estado (`self.df`, `self.metricas`...) entre as etapas; **métodos** = as etapas.
- `if __name__ == "__main__":` roda `main()` só quando o arquivo é executado direto (não quando importado).
- Ordem: carregar → inspecionar → transformar (limpa antes!) → analisar → visualizar → resumo.
- ❓ P10: o que acontece com `main()` se outro arquivo fizer `import salesinsight`?

## Git (Semana 04)
- `main` = versão estável; `develop` = integração; `feat/...` = uma funcionalidade; `docs/...` = documentação.
- Commit = foto do projeto com mensagem (`feat:`, `fix:`, `docs:`). Mínimo 5 commits (individual).

---

## Respostas
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
período. Eram 6 de 200 registros (3%), e a perda aparece no relatório de limpeza."
