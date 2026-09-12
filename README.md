# Dashboard de Performance de Mídia Paga

Dashboard em Streamlit que transforma um CSV bruto de campanhas (Google Ads, Meta Ads, Amazon Ads, TikTok Ads etc.) em um painel executivo: KPIs, evolução de investimento x receita, ROAS por canal e ranking de campanhas.

## Por que existe

Template pronto para oferecer como serviço a agências e e-commerces que ainda consolidam performance manualmente em planilha. O cliente sobe o export bruto (ou uma versão já padronizada) e recebe o dashboard pronto, sem precisar mexer em código.

## O que faz

- Upload de CSV (ou dados de exemplo pré-carregados, para demonstração)
- Validação do arquivo com mensagens de erro claras (coluna faltando, data em formato errado, valor não numérico)
- Filtros por período, canal e campanha
- KPIs: Investimento, Receita, ROAS, CPA, CTR, Taxa de Conversão
- Gráfico de investimento x receita ao longo do tempo
- Gráfico de ROAS por canal
- Ranking de campanhas (ordenado por receita) com ROAS e CPA calculados
- Exportação dos dados filtrados em CSV

## Formato do CSV esperado

```
Data,Canal,Campanha,Investimento,Impressões,Cliques,Conversões,Receita
2026-06-15,Google Ads,Pesquisa - Marca,358.28,5801,203,4,451.42
```

- `Data`: formato AAAA-MM-DD
- `Canal`: nome da plataforma (Google Ads, Meta Ads, Amazon Ads, ML Ads, VTEX Ads etc.)
- `Campanha`: nome da campanha
- `Investimento`, `Receita`: valores em R$, número puro (sem "R$" ou separador de milhar)
- `Impressões`, `Cliques`, `Conversões`: números inteiros

Cada plataforma exporta relatório em formato diferente — a ideia é padronizar (manualmente ou com uma automação futura) para essas 8 colunas antes de subir aqui.

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre com dados de exemplo sintéticos (gerados em memória — 90 dias, 4 canais, 3 campanhas por canal) — dá pra ver o dashboard funcionando sem precisar de dado real. Para usar dados reais, desative "Usar dados de exemplo" na barra lateral e suba o seu CSV.

Quer gerar um CSV de exemplo em arquivo (pra testar o fluxo de upload)? Rode `python3 gerar_dados_exemplo.py` — cria `sample_data.csv` com os mesmos dados sintéticos.

## Stack

Python, Streamlit, Pandas, Plotly.

## Status

Funcional e testado localmente (upload, validação, filtros, gráficos e export todos rodando). Ainda não publicado com URL própria — pronto para deploy no Streamlit Community Cloud quando fizer sentido oferecer a um cliente.
