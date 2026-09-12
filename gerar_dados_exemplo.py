"""
Gera um CSV de exemplo (dados sintéticos) no formato que o dashboard espera.
Simula 90 dias de mídia paga para um e-commerce brasileiro fictício,
com 4 canais e 3 campanhas por canal.

Rodar: python3 gerar_dados_exemplo.py
Gera: sample_data.csv
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

CANAIS = {
    "Google Ads":  {"campanhas": ["Pesquisa - Marca", "Pesquisa - Genérico", "Performance Max"], "cpc_base": 1.8, "ctr_base": 0.045},
    "Meta Ads":    {"campanhas": ["Prospecção - Lookalike", "Remarketing - Carrinho", "Catálogo - Dinâmico"], "cpc_base": 1.1, "ctr_base": 0.018},
    "Amazon Ads":  {"campanhas": ["Sponsored Products", "Sponsored Brands", "Sponsored Display"], "cpc_base": 1.4, "ctr_base": 0.032},
    "TikTok Ads":  {"campanhas": ["Spark Ads - UGC", "Prospecção - Interesse", "Retargeting"], "cpc_base": 0.9, "ctr_base": 0.021},
}

dias = pd.date_range(end=datetime.today(), periods=90, freq="D")

linhas = []
for canal, cfg in CANAIS.items():
    for campanha in cfg["campanhas"]:
        # sazonalidade leve + tendência de fim de semana mais fraco em B2C
        for dia in dias:
            fator_fds = 0.75 if dia.weekday() >= 5 else 1.0
            fator_ruido = np.random.normal(1, 0.18)
            fator_ruido = max(0.3, fator_ruido)

            investimento = round(np.random.uniform(80, 420) * fator_fds * fator_ruido, 2)
            cpc = max(0.25, np.random.normal(cfg["cpc_base"], cfg["cpc_base"] * 0.15))
            cliques = max(0, int(investimento / cpc))
            ctr = max(0.003, np.random.normal(cfg["ctr_base"], cfg["ctr_base"] * 0.2))
            impressoes = int(cliques / ctr) if ctr > 0 else 0
            taxa_conv = np.random.uniform(0.015, 0.06)
            conversoes = int(cliques * taxa_conv)
            ticket_medio = np.random.uniform(90, 340)
            receita = round(conversoes * ticket_medio * np.random.normal(1, 0.25), 2)
            receita = max(0, receita)

            linhas.append({
                "Data": dia.strftime("%Y-%m-%d"),
                "Canal": canal,
                "Campanha": campanha,
                "Investimento": investimento,
                "Impressões": impressoes,
                "Cliques": cliques,
                "Conversões": conversoes,
                "Receita": receita,
            })

df = pd.DataFrame(linhas)
df.to_csv("sample_data.csv", index=False, encoding="utf-8-sig")
print(f"Gerado sample_data.csv com {len(df)} linhas, {df['Data'].min()} a {df['Data'].max()}")
