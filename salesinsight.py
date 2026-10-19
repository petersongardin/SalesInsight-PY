"""SalesInsight PY - Analise e Visualizacao de Dados de Vendas.

Fluxo: gerar/carregar -> inspecionar -> limpar -> derivar colunas ->
agregar -> segmentar -> visualizar -> exportar.
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


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


if __name__ == "__main__":
    # teste provisorio das etapas ja escritas (main() completa vem no RF10)
    bruto = gerar_dataset_vendas()
    bruto.to_csv("vendas.csv", index=False)
    inspecionar_dados(pd.read_csv("vendas.csv"))
