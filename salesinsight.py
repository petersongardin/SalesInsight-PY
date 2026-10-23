"""SalesInsight PY - Analise e Visualizacao de Dados de Vendas.

Fluxo: gerar/carregar -> inspecionar -> limpar -> derivar colunas ->
agregar -> segmentar -> visualizar -> exportar.
"""
import json
import os
import random
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # backend sem janela: so grava arquivos PNG
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PASTA_SAIDA = "outputs"
PASTA_GRAFICOS = os.path.join(PASTA_SAIDA, "graficos")
MESES_PT = {1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}


# ---------------------------------------------------------------------------
# RF01 - Criar ou carregar o dataset
# ---------------------------------------------------------------------------
def gerar_dataset_vendas(n_registros=200, seed=42):
    """Gera um dataset sintetico de vendas com datas invalidas propositais.

    A seed fixa garante que qualquer pessoa gere exatamente os mesmos dados
    (reprodutibilidade).
    """
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor",
                "Teclado", "Mouse", "Headset"]
    # dicionario: chave (produto) -> valor (categoria / preco base)
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120,
              "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]

    data_inicio = datetime(2025, 1, 1)
    dados = []  # lista de dicionarios: cada dict vira uma linha do DataFrame

    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        # preco varia de -15% a +15% em torno do preco base
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        data_txt = data.strftime("%Y-%m-%d")
        cliente = f"Cliente_{random.randint(1, 50):03d}"

        # --- sujeira proposital para a etapa de limpeza (~3% dos registros) ---
        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"

        dados.append({
            "id_venda": i + 1,
            "data_venda": data_txt,
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    return pd.DataFrame(dados)


# ---------------------------------------------------------------------------
# RF02 - Inspecionar e descrever os dados
# ---------------------------------------------------------------------------
def inspecionar_dados(df):
    """Exibe as informacoes estruturais do DataFrame (sem estatisticas)."""
    print("\n=== INSPECAO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df


# ---------------------------------------------------------------------------
# RF03 - Tratar os dados (datetime)
# ---------------------------------------------------------------------------
def tratar_dados(df):
    """Limpa o DataFrame de vendas.

    Retorna (df_limpo, relatorio). So padroniza texto e converte tipos;
    nao imputa nulos nem remove outliers (conteudo das semanas 09-11).
    """
    df = df.copy()  # nao altera o DataFrame original
    relatorio = {"registros_iniciais": len(df)}

    # 1. espacos extras nas colunas de texto
    colunas_texto = ["data_venda", "cliente", "produto", "categoria", "regiao"]
    for coluna in colunas_texto:
        df[coluna] = df[coluna].astype(str).str.strip()

    # 2. datas: o que nao converte vira NaT e a linha e removida
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    invalidas = int(df["data_venda"].isnull().sum())
    df = df.dropna(subset=["data_venda"])

    # 3. tipos numericos: quantidade -> int, preco_unitario -> float
    tipos_antes = df.dtypes.astype(str).to_dict()
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)
    tipos_depois = df.dtypes.astype(str).to_dict()
    convertidos_tipo = sum(
        1 for c in ("quantidade", "preco_unitario")
        if tipos_antes[c] != tipos_depois[c])

    # 4. relatorio
    relatorio["datas_invalidas_removidas"] = invalidas
    relatorio["colunas_com_tipo_convertido"] = convertidos_tipo
    relatorio["registros_finais"] = len(df)
    relatorio["registros_sem_alteracao"] = (
        relatorio["registros_iniciais"] - invalidas)

    print("\n=== RELATORIO DE LIMPEZA ===")
    print(f"Registros que entraram:          {relatorio['registros_iniciais']}")
    print(f"Removidos (data invalida):       {invalidas}")
    print(f"Colunas com tipo convertido:     {convertidos_tipo}")
    print(f"Registros mantidos sem remocao:  {relatorio['registros_sem_alteracao']}")
    print(f"Registros finais:                {relatorio['registros_finais']}")
    return df.reset_index(drop=True), relatorio


# ---------------------------------------------------------------------------
# RF04 - Colunas derivadas
# ---------------------------------------------------------------------------
def criar_colunas_derivadas(df):
    """Cria receita_total, mes, mes_nome, trimestre, ano e faixa_receita_item."""
    df = df.copy()
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]  # vetorizado
    df["mes"] = df["data_venda"].dt.month
    df["mes_nome"] = df["mes"].map(MESES_PT)  # dicionario, nao %B (ingles)
    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)
    df["ano"] = df["data_venda"].dt.year

    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    faixas = ["Baixo Valor", "Medio Valor", "Alto Valor"]
    df["faixa_receita_item"] = np.select(condicoes, faixas,
                                         default="Nao Classificado")
    return df


# ---------------------------------------------------------------------------
# RF08 - Funcao de ordem superior (recebe outra funcao como argumento)
# ---------------------------------------------------------------------------
def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """Aplica `funcao_transformacao` a cada valor de `coluna`."""
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df


# ---------------------------------------------------------------------------
# RF05 - Metricas agregadas
# ---------------------------------------------------------------------------
def calcular_metricas(df):
    """Retorna {nome_da_metrica: DataFrame} com as agregacoes do projeto."""
    metricas = {}

    metricas["por_mes"] = (
        df.groupby("mes")
        .agg(receita_total=("receita_total", "sum"),
             quantidade=("quantidade", "sum"),
             n_vendas=("id_venda", "count"))
        .reset_index())

    metricas["por_trimestre"] = (
        df.groupby("trimestre")
        .agg(receita_total=("receita_total", "sum"),
             n_vendas=("id_venda", "count"))
        .reset_index())

    metricas["top_produtos"] = (
        df.groupby("produto")["receita_total"].sum()
        .sort_values(ascending=False).head(5).reset_index())

    metricas["por_categoria"] = (
        df.groupby("categoria")["receita_total"].sum()
        .sort_values(ascending=False).reset_index())

    metricas["por_regiao"] = (
        df.groupby("regiao")
        .agg(receita_total=("receita_total", "sum"),
             ticket_medio=("receita_total", "mean"))
        .sort_values("receita_total", ascending=False).reset_index())

    for nome, tabela in metricas.items():
        print(f"\n=== {nome.upper().replace('_', ' ')} ===")
        print(tabela.round(2).to_string(index=False))
    return metricas


# ---------------------------------------------------------------------------
# RF06 - Segmentacao de clientes
# ---------------------------------------------------------------------------
def segmentar_clientes(df):
    """Soma o gasto por cliente e classifica em Bronze / Prata / Ouro."""
    clientes = (df.groupby("cliente")["receita_total"].sum()
                .reset_index(name="total_gasto"))
    # lambda #1: regra de segmento aplicada linha a linha com .apply()
    clientes["segmento"] = clientes["total_gasto"].apply(
        lambda v: "Bronze" if v < 5000 else ("Prata" if v <= 15000 else "Ouro"))
    clientes = clientes.sort_values("total_gasto", ascending=False)
    clientes = clientes.reset_index(drop=True)

    print("\n=== TOP 10 CLIENTES ===")
    print(clientes.head(10).round(2).to_string(index=False))
    print("\n=== CLIENTES POR SEGMENTO ===")
    print(clientes["segmento"].value_counts())
    return clientes


# ---------------------------------------------------------------------------
# RF07 - Visualizacoes
# ---------------------------------------------------------------------------
CORES_CATEGORIA = {"Computadores": "#1f4e79", "Celulares": "#e07b00",
                   "Perifericos": "#2e8b57"}
COR_PRINCIPAL = "#1f4e79"


def configurar_estilo():
    """Define o tema global dos graficos."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 14


def _salvar(fig, nome):
    """Ajusta layout, grava PNG (dpi 150) e fecha a figura."""
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_GRAFICOS, nome), dpi=150)
    plt.close(fig)


def grafico_receita_por_mes(por_mes):
    """Figura 1 - linha: receita total por mes."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(por_mes["mes"], por_mes["receita_total"], marker="o",
            linewidth=2, color=COR_PRINCIPAL, label="Receita total")
    ax.set_title("Receita Total por Mes")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Receita Total (R$)")
    ax.set_xticks(range(1, 13))
    ax.legend()
    _salvar(fig, "receita_por_mes.png")


def grafico_top_produtos(top_produtos):
    """Figura 2 - barras horizontais: top 5 produtos por receita."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_produtos, y="produto", x="receita_total",
                hue="produto", legend=False, palette="Blues_r", ax=ax)
    ax.set_title("Top 5 Produtos por Receita")
    ax.set_xlabel("Receita Total (R$)")
    ax.set_ylabel("Produto")
    _salvar(fig, "top_produtos.png")


def grafico_quantidade_vs_receita(df):
    """Figura 3 - dispersao: quantidade x receita, cor por categoria."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x="quantidade", y="receita_total",
                    hue="categoria", palette=CORES_CATEGORIA, s=70, ax=ax)
    ax.set_title("Quantidade x Receita por Transacao")
    ax.set_xlabel("Quantidade vendida")
    ax.set_ylabel("Receita da transacao (R$)")
    ax.legend(title="Categoria")
    _salvar(fig, "quantidade_vs_receita.png")


def grafico_painel_resumo(df, metricas):
    """Figura 4 - painel 2x2 combinando as visoes anteriores + regiao."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    por_mes, top = metricas["por_mes"], metricas["top_produtos"]
    regiao = metricas["por_regiao"]

    axes[0, 0].plot(por_mes["mes"], por_mes["receita_total"], marker="o",
                    color=COR_PRINCIPAL, label="Receita")
    axes[0, 0].set_title("Receita por Mes")
    axes[0, 0].set_xlabel("Mes")
    axes[0, 0].set_ylabel("Receita (R$)")
    axes[0, 0].legend()

    axes[0, 1].bar(top["produto"], top["receita_total"], color="#2e75b6")
    axes[0, 1].set_title("Top 5 Produtos")
    axes[0, 1].set_xlabel("Produto")
    axes[0, 1].set_ylabel("Receita (R$)")
    axes[0, 1].tick_params(axis="x", rotation=30)

    for categoria, grupo in df.groupby("categoria"):
        axes[1, 0].scatter(grupo["quantidade"], grupo["receita_total"],
                           color=CORES_CATEGORIA[categoria], label=categoria,
                           alpha=0.7)
    axes[1, 0].set_title("Quantidade x Receita")
    axes[1, 0].set_xlabel("Quantidade")
    axes[1, 0].set_ylabel("Receita (R$)")
    axes[1, 0].legend(title="Categoria")

    axes[1, 1].bar(regiao["regiao"], regiao["receita_total"], color="#e07b00")
    axes[1, 1].set_title("Receita por Regiao")
    axes[1, 1].set_xlabel("Regiao")
    axes[1, 1].set_ylabel("Receita (R$)")
    axes[1, 1].tick_params(axis="x", rotation=30)

    fig.suptitle("SalesInsight PY - Painel Resumo", fontsize=16)
    _salvar(fig, "painel_resumo.png")


# ---------------------------------------------------------------------------
# BONUS B04 - Regressao linear simples (conteudo da Semana 13, nao exigido)
# ---------------------------------------------------------------------------
def grafico_regressao_bonus(df):
    """Ajusta receita_total = a * quantidade + b por categoria e desenha as retas.

    Variavel independente (X): quantidade. Variavel dependente (Y): receita_total.
    Retorna um DataFrame com inclinacao (a), intercepto (b) e R2 de cada categoria.
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    xs = np.linspace(1, 10, 50)
    linhas = []
    for categoria, grupo in df.groupby("categoria"):
        x, y = grupo["quantidade"], grupo["receita_total"]
        inclinacao, intercepto = np.polyfit(x, y, 1)
        r2 = np.corrcoef(x, y)[0, 1] ** 2
        cor = CORES_CATEGORIA[categoria]
        ax.scatter(x, y, color=cor, alpha=0.5, s=50)
        ax.plot(xs, inclinacao * xs + intercepto, color=cor, linewidth=2.5,
                label=f"{categoria}: y = {inclinacao:.0f}x {intercepto:+.0f}"
                      f"  (R² = {r2:.2f})")
        linhas.append({"categoria": categoria, "inclinacao": round(inclinacao, 2),
                       "intercepto": round(intercepto, 2), "r2": round(r2, 3)})
    ax.set_title("Bonus: Regressao Linear - Receita em funcao da Quantidade")
    ax.set_xlabel("Quantidade vendida (variavel independente X)")
    ax.set_ylabel("Receita da transacao em R$ (variavel dependente Y)")
    ax.legend(title="Reta ajustada por categoria")
    _salvar(fig, "bonus_regressao.png")

    coeficientes = pd.DataFrame(linhas)
    print("\n=== BONUS: REGRESSAO RECEITA x QUANTIDADE ===")
    print(coeficientes.to_string(index=False))
    return coeficientes


# ---------------------------------------------------------------------------
# RF09 - Exportacao CSV e JSON
# ---------------------------------------------------------------------------
def exportar_resultados(metricas, clientes, estatisticas):
    """Grava CSVs e JSON e le o JSON de volta para conferencia."""
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    metricas["por_mes"].to_csv(
        os.path.join(PASTA_SAIDA, "metricas_por_mes.csv"),
        index=False, encoding="utf-8-sig")
    clientes.to_csv(
        os.path.join(PASTA_SAIDA, "segmentacao_clientes.csv"),
        index=False, encoding="utf-8-sig")

    serializavel = {k: round(float(v), 2) for k, v in estatisticas.items()}
    caminho = os.path.join(PASTA_SAIDA, "estatisticas_gerais.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(serializavel, f, indent=4, ensure_ascii=False)

    with open(caminho, "r", encoding="utf-8") as f:
        conferencia = json.load(f)
    print(f"\nJSON gravado e lido de volta: {conferencia}")
    return conferencia


# ---------------------------------------------------------------------------
# Classe que organiza o fluxo
# ---------------------------------------------------------------------------
class AnalisadorDeVendas:
    """Guarda o estado do fluxo (dados, metricas, clientes) entre as etapas."""

    def __init__(self):
        self.df_bruto = None
        self.df = None
        self.relatorio = None
        self.metricas = None
        self.clientes = None

    def carregar(self, caminho):
        """Le o CSV bruto."""
        self.df_bruto = pd.read_csv(caminho)
        return self.df_bruto

    def transformar(self):
        """Limpeza ANTES das derivadas (ordem exigida pelo RF10)."""
        df, self.relatorio = tratar_dados(self.df_bruto)
        df = criar_colunas_derivadas(df)
        df = processar_coluna(df, "receita_total",
                              lambda x: round(x / 1000, 2),  # lambda #2
                              nome_saida="receita_em_milhares")
        df = processar_coluna(
            df, "quantidade",
            lambda q: "Alto Volume" if q > 5 else "Baixo Volume",  # lambda #3
            nome_saida="perfil_volume")
        self.df = df
        return df

    def analisar(self):
        """Agrega metricas e segmenta clientes."""
        self.metricas = calcular_metricas(self.df)
        self.clientes = segmentar_clientes(self.df)

    def visualizar(self):
        """Gera as 4 figuras PNG obrigatorias e o grafico bonus de regressao."""
        configurar_estilo()
        grafico_receita_por_mes(self.metricas["por_mes"])
        grafico_top_produtos(self.metricas["top_produtos"])
        grafico_quantidade_vs_receita(self.df)
        grafico_painel_resumo(self.df, self.metricas)
        grafico_regressao_bonus(self.df)
        print(f"\n5 graficos salvos em {PASTA_GRAFICOS}/ (4 obrigatorios + 1 bonus)")

    def resumo(self):
        """Monta estatisticas gerais e exporta tudo."""
        estatisticas = {
            "receita_total": self.df["receita_total"].sum(),
            "ticket_medio": self.df["receita_total"].mean(),
            "n_vendas": len(self.df),
            "n_clientes": self.df["cliente"].nunique(),
            "linhas_removidas": self.relatorio["datas_invalidas_removidas"],
        }
        exportar_resultados(self.metricas, self.clientes, estatisticas)


# ---------------------------------------------------------------------------
# RF10 - Ponto de entrada
# ---------------------------------------------------------------------------
def main():
    """Executa o fluxo completo do SalesInsight PY."""
    print("=" * 60)
    print("   SALESINSIGHT PY - Analise de Dados de Vendas")
    print("=" * 60)

    if not os.path.exists("vendas.csv"):
        gerar_dataset_vendas().to_csv("vendas.csv", index=False)

    analisador = AnalisadorDeVendas()
    analisador.carregar("vendas.csv")
    inspecionar_dados(analisador.df_bruto)
    analisador.transformar()
    analisador.analisar()
    analisador.visualizar()
    analisador.resumo()

    print("\n[CONCLUIDO] Fluxo finalizado com sucesso.")


if __name__ == "__main__":
    main()
