import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Dashboard de Performance", page_icon="📊", layout="wide")

COLUNAS_ESPERADAS = ["Data", "Canal", "Campanha", "Investimento", "Impressões", "Cliques", "Conversões", "Receita"]

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.7rem; }
.bloco-titulo { font-size: 1.05rem; font-weight: 600; margin: 1.2rem 0 0.4rem; color: #333; }
.rodape-nota { font-size: 0.78rem; color: #888; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Performance de Mídia Paga")
st.caption("Suba o export bruto das suas campanhas e receba KPIs, gráficos e ranking de campanhas em segundos.")

# ══════════════════════════════════════════════════════════════
# SIDEBAR — FONTE DE DADOS
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Dados")
    usar_exemplo = st.toggle("Usar dados de exemplo", value=True,
                              help="Desative para subir o seu próprio arquivo CSV.")

    arquivo = None
    if not usar_exemplo:
        arquivo = st.file_uploader("CSV de campanhas", type=["csv"])
        with st.expander("📋 Formato esperado do CSV"):
            st.code(",".join(COLUNAS_ESPERADAS), language=None)
            st.markdown(
                "- **Data**: formato AAAA-MM-DD\n"
                "- **Canal**: ex. Google Ads, Meta Ads, Amazon Ads\n"
                "- **Campanha**: nome da campanha\n"
                "- **Investimento, Receita**: valores em R$ (número, sem símbolo)\n"
                "- **Impressões, Cliques, Conversões**: números inteiros"
            )
        st.download_button(
            "⬇️ Baixar modelo de CSV",
            data=",".join(COLUNAS_ESPERADAS) + "\n",
            file_name="modelo_dashboard.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════════════════════
# CARGA E VALIDAÇÃO DE DADOS
# ══════════════════════════════════════════════════════════════
@st.cache_data
def carregar_exemplo():
    """Gera dados sintéticos de exemplo em memória (90 dias, 4 canais, 3 campanhas por canal).
    Mesma lógica de gerar_dados_exemplo.py — mantida aqui pra o app funcionar sem depender de um CSV salvo."""
    rng = np.random.default_rng(42)
    canais = {
        "Google Ads":  {"campanhas": ["Pesquisa - Marca", "Pesquisa - Genérico", "Performance Max"], "cpc_base": 1.8, "ctr_base": 0.045},
        "Meta Ads":    {"campanhas": ["Prospecção - Lookalike", "Remarketing - Carrinho", "Catálogo - Dinâmico"], "cpc_base": 1.1, "ctr_base": 0.018},
        "Amazon Ads":  {"campanhas": ["Sponsored Products", "Sponsored Brands", "Sponsored Display"], "cpc_base": 1.4, "ctr_base": 0.032},
        "TikTok Ads":  {"campanhas": ["Spark Ads - UGC", "Prospecção - Interesse", "Retargeting"], "cpc_base": 0.9, "ctr_base": 0.021},
    }
    dias = pd.date_range(end=datetime.today(), periods=90, freq="D")
    linhas = []
    for canal, cfg in canais.items():
        for campanha in cfg["campanhas"]:
            for dia in dias:
                fator_fds = 0.75 if dia.weekday() >= 5 else 1.0
                fator_ruido = max(0.3, rng.normal(1, 0.18))
                investimento = round(rng.uniform(80, 420) * fator_fds * fator_ruido, 2)
                cpc = max(0.25, rng.normal(cfg["cpc_base"], cfg["cpc_base"] * 0.15))
                cliques = max(0, int(investimento / cpc))
                ctr = max(0.003, rng.normal(cfg["ctr_base"], cfg["ctr_base"] * 0.2))
                impressoes = int(cliques / ctr) if ctr > 0 else 0
                taxa_conv = rng.uniform(0.015, 0.06)
                conversoes = int(cliques * taxa_conv)
                ticket_medio = rng.uniform(90, 340)
                receita = max(0, round(conversoes * ticket_medio * rng.normal(1, 0.25), 2))
                linhas.append({
                    "Data": dia.strftime("%Y-%m-%d"), "Canal": canal, "Campanha": campanha,
                    "Investimento": investimento, "Impressões": impressoes, "Cliques": cliques,
                    "Conversões": conversoes, "Receita": receita,
                })
    return pd.DataFrame(linhas)

def validar_e_preparar(df: pd.DataFrame):
    faltando = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    if faltando:
        return None, f"Colunas faltando no CSV: {', '.join(faltando)}"
    df = df.copy()
    try:
        df["Data"] = pd.to_datetime(df["Data"])
    except Exception:
        return None, "Não consegui converter a coluna 'Data'. Use o formato AAAA-MM-DD."
    numericas = ["Investimento", "Impressões", "Cliques", "Conversões", "Receita"]
    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[numericas].isna().any().any():
        return None, "Encontrei valores não numéricos em Investimento/Impressões/Cliques/Conversões/Receita. Confira o arquivo."
    return df, None

df_raw = None
erro = None

if usar_exemplo:
    df_raw = carregar_exemplo()
    df_raw["Data"] = pd.to_datetime(df_raw["Data"])
elif arquivo is not None:
    try:
        df_bruto = pd.read_csv(arquivo)
    except Exception as e:
        erro = f"Não consegui ler o arquivo: {e}"
    else:
        df_raw, erro = validar_e_preparar(df_bruto)

if erro:
    st.error(f"⚠️ {erro}")
    st.stop()

if df_raw is None:
    st.info("👈 Suba um CSV na barra lateral (ou deixe 'Usar dados de exemplo' ativado) para ver o dashboard.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# FILTROS
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="bloco-titulo">Filtros</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 2, 3])

with f1:
    data_min, data_max = df_raw["Data"].min().date(), df_raw["Data"].max().date()
    periodo = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
with f2:
    canais_disp = sorted(df_raw["Canal"].unique())
    canais_sel = st.multiselect("Canal", canais_disp, default=canais_disp)
with f3:
    campanhas_disp = sorted(df_raw[df_raw["Canal"].isin(canais_sel)]["Campanha"].unique())
    campanhas_sel = st.multiselect("Campanha", campanhas_disp, default=campanhas_disp)

if isinstance(periodo, tuple) and len(periodo) == 2:
    ini, fim = periodo
else:
    ini, fim = data_min, data_max

df = df_raw[
    (df_raw["Data"].dt.date >= ini) &
    (df_raw["Data"].dt.date <= fim) &
    (df_raw["Canal"].isin(canais_sel)) &
    (df_raw["Campanha"].isin(campanhas_sel))
].copy()

if df.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# MÉTRICAS DERIVADAS
# ══════════════════════════════════════════════════════════════
investimento_total = df["Investimento"].sum()
receita_total = df["Receita"].sum()
cliques_total = df["Cliques"].sum()
impressoes_total = df["Impressões"].sum()
conversoes_total = df["Conversões"].sum()

roas = (receita_total / investimento_total) if investimento_total > 0 else 0
cpa = (investimento_total / conversoes_total) if conversoes_total > 0 else 0
cpc = (investimento_total / cliques_total) if cliques_total > 0 else 0
ctr = (cliques_total / impressoes_total * 100) if impressoes_total > 0 else 0
taxa_conv = (conversoes_total / cliques_total * 100) if cliques_total > 0 else 0

# ══════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="bloco-titulo">Visão geral do período</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Investimento", f"R$ {investimento_total:,.0f}".replace(",", "."))
k2.metric("Receita", f"R$ {receita_total:,.0f}".replace(",", "."))
k3.metric("ROAS", f"{roas:.2f}x")
k4.metric("CPA", f"R$ {cpa:,.2f}".replace(",", "."))
k5.metric("CTR", f"{ctr:.2f}%")
k6.metric("Tx. Conversão", f"{taxa_conv:.2f}%")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# GRÁFICO: INVESTIMENTO x RECEITA AO LONGO DO TEMPO
# ══════════════════════════════════════════════════════════════
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown('<div class="bloco-titulo">Investimento x Receita por dia</div>', unsafe_allow_html=True)
    serie = df.groupby("Data", as_index=False)[["Investimento", "Receita"]].sum()
    fig_serie = go.Figure()
    fig_serie.add_trace(go.Scatter(x=serie["Data"], y=serie["Investimento"], name="Investimento", line=dict(color="#ef4444")))
    fig_serie.add_trace(go.Scatter(x=serie["Data"], y=serie["Receita"], name="Receita", line=dict(color="#0ea5e9")))
    fig_serie.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_serie, use_container_width=True)

with col_b:
    st.markdown('<div class="bloco-titulo">ROAS por canal</div>', unsafe_allow_html=True)
    por_canal = df.groupby("Canal", as_index=False)[["Investimento", "Receita"]].sum()
    por_canal["ROAS"] = por_canal["Receita"] / por_canal["Investimento"].replace(0, pd.NA)
    fig_canal = px.bar(por_canal.sort_values("ROAS"), x="ROAS", y="Canal", orientation="h",
                        color="ROAS", color_continuous_scale="Blues", text_auto=".2f")
    fig_canal.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_canal, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# TABELA: RANKING DE CAMPANHAS
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="bloco-titulo">Ranking de campanhas</div>', unsafe_allow_html=True)

por_campanha = df.groupby(["Canal", "Campanha"], as_index=False).agg(
    Investimento=("Investimento", "sum"),
    Receita=("Receita", "sum"),
    Cliques=("Cliques", "sum"),
    Conversões=("Conversões", "sum"),
)
por_campanha["ROAS"] = (por_campanha["Receita"] / por_campanha["Investimento"].replace(0, pd.NA)).round(2)
por_campanha["CPA"] = (por_campanha["Investimento"] / por_campanha["Conversões"].replace(0, pd.NA)).round(2)
por_campanha = por_campanha.sort_values("Receita", ascending=False)

st.dataframe(
    por_campanha.style.format({
        "Investimento": "R$ {:,.2f}",
        "Receita": "R$ {:,.2f}",
        "CPA": "R$ {:,.2f}",
        "ROAS": "{:.2f}x",
    }),
    use_container_width=True,
    hide_index=True,
)

# ══════════════════════════════════════════════════════════════
# EXPORTAR
# ══════════════════════════════════════════════════════════════
csv_export = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Baixar dados filtrados (CSV)", data=csv_export, file_name="performance_filtrada.csv", mime="text/csv")

st.markdown(
    '<div class="rodape-nota">Template de dashboard — Paulo Santos (Growth AI). '
    'Feito para agências e e-commerces analisarem performance de mídia paga sem depender de planilha manual.</div>',
    unsafe_allow_html=True,
)
