import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ENEM 2024 · Henrique Coutinho",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Tema visual — fundo escuro slate, acentos âmbar
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background-color: #0f1117;
    color: #e8eaf0;
}

section[data-testid="stSidebar"] {
    background-color: #1a1d27;
    border-right: 1px solid #2e3147;
}

/* Cabeçalho customizado */
.hc-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
}
.hc-title {
    font-size: 2rem;
    font-weight: 700;
    color: #f5c842;
    letter-spacing: -0.5px;
}
.hc-sub {
    font-size: 0.9rem;
    color: #7b7f9e;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* Cards de métrica */
.metric-card {
    background: #1a1d27;
    border: 1px solid #2e3147;
    border-radius: 10px;
    padding: 18px 22px;
    text-align: center;
}
.metric-label {
    font-size: 0.75rem;
    color: #7b7f9e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f5c842;
}

/* Divisor sutil */
hr.hc-divider {
    border: none;
    border-top: 1px solid #2e3147;
    margin: 24px 0;
}

/* Tabela */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Conexão com banco
# ---------------------------------------------------------------------------
engine = create_engine("postgresql://data_iesb:iesb@bigdata.dataiesb.com/iesb")

@st.cache_data
def load_data() -> pd.DataFrame:
    query = "SELECT sg_uf_esc, nota_media_5_notas FROM ed_enem_2024_resultados_amos_per"
    return pd.read_sql(query, engine)

df = load_data()

# ---------------------------------------------------------------------------
# Sidebar — Filtros
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)

    ufs_ordenadas = sorted(df["sg_uf_esc"].dropna().unique())
    ufs = st.multiselect(
        "Estados (UF):",
        options=ufs_ordenadas,
        default=ufs_ordenadas,
    )

    min_nota = float(df["nota_media_5_notas"].min())
    max_nota = float(df["nota_media_5_notas"].max())

    nota_min, nota_max = st.slider(
        "Faixa de nota média:",
        min_value=min_nota,
        max_value=max_nota,
        value=(min_nota, max_nota),
        step=0.5,
    )

    st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)
    st.caption("Henrique Coutinho · ENEM 2024")

# ---------------------------------------------------------------------------
# Filtro aplicado
# ---------------------------------------------------------------------------
df_filtrado = df[
    df["sg_uf_esc"].isin(ufs)
    & df["nota_media_5_notas"].between(nota_min, nota_max)
].copy()

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hc-header">
    <span class="hc-title">ENEM 2024</span>
    <span class="hc-sub">Análise por Henrique Coutinho</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Corpo principal
# ---------------------------------------------------------------------------
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- 1. Métricas ---
m1, m2, m3, m4 = st.columns(4)

def metric_card(col, label, value):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

metric_card(m1, "Total de alunos",   f"{len(df_filtrado):,}".replace(",", "."))
metric_card(m2, "Média geral",       f"{df_filtrado['nota_media_5_notas'].mean():.2f}")
metric_card(m3, "Mediana",           f"{df_filtrado['nota_media_5_notas'].median():.2f}")
metric_card(m4, "Nota máxima",       f"{df_filtrado['nota_media_5_notas'].max():.2f}")

st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)

# --- 2. Linha superior: Violin + Scatter de médias por UF ---
col_a, col_b = st.columns(2)

PLOT_BG  = "#0f1117"
PAPER_BG = "#0f1117"
FONT_CLR = "#e8eaf0"
GRID_CLR = "#2e3147"
AMBER    = "#f5c842"

base_layout = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font_color=FONT_CLR,
    xaxis=dict(gridcolor=GRID_CLR, showgrid=True),
    yaxis=dict(gridcolor=GRID_CLR, showgrid=True),
    margin=dict(l=40, r=20, t=50, b=40),
)

with col_a:
    # Violin — substitui o box plot
    fig_violin = px.violin(
        df_filtrado,
        x="sg_uf_esc",
        y="nota_media_5_notas",
        box=True,
        points=False,
        title="Distribuição de Notas por UF (Violin)",
        labels={"sg_uf_esc": "UF", "nota_media_5_notas": "Nota Média"},
        color_discrete_sequence=["#f5c842"],
    )
    fig_violin.update_layout(**base_layout, showlegend=False)
    st.plotly_chart(fig_violin, use_container_width=True)

with col_b:
    # Scatter: média vs desvio-padrão por UF — substitui o bar chart
    stats_uf = (
        df_filtrado.groupby("sg_uf_esc")["nota_media_5_notas"]
        .agg(media="mean", desvio="std", total="count")
        .reset_index()
        .rename(columns={"sg_uf_esc": "UF"})
    )

    fig_scatter = px.scatter(
        stats_uf,
        x="media",
        y="desvio",
        size="total",
        text="UF",
        title="Média vs. Dispersão por UF",
        labels={"media": "Nota Média", "desvio": "Desvio Padrão", "total": "Alunos"},
        color="media",
        color_continuous_scale="YlOrBr",
    )
    fig_scatter.update_traces(textposition="top center", textfont_size=10)
    fig_scatter.update_layout(**base_layout)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)

# --- 3. Heatmap de notas por faixa e UF — substitui o histograma ---
st.subheader("Mapa de Calor · Concentração de Notas por UF")

bins = list(range(int(nota_min), int(nota_max) + 2, 50)) or [int(nota_min), int(nota_max) + 1]
df_filtrado["faixa"] = pd.cut(
    df_filtrado["nota_media_5_notas"],
    bins=bins,
    right=False,
).astype(str)

heat_data = (
    df_filtrado.groupby(["sg_uf_esc", "faixa"])
    .size()
    .reset_index(name="qtd")
    .pivot(index="faixa", columns="sg_uf_esc", values="qtd")
    .fillna(0)
)

fig_heat = go.Figure(
    go.Heatmap(
        z=heat_data.values,
        x=heat_data.columns.tolist(),
        y=heat_data.index.tolist(),
        colorscale="YlOrBr",
        hoverongaps=False,
        colorbar=dict(title="Alunos", tickfont=dict(color=FONT_CLR)),
    )
)
fig_heat.update_layout(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font_color=FONT_CLR,
    xaxis_title="UF",
    yaxis_title="Faixa de Nota",
    margin=dict(l=80, r=20, t=20, b=60),
    height=380,
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("<hr class='hc-divider'>", unsafe_allow_html=True)

# --- 4. Resumo estatístico ---
st.subheader("Resumo Estatístico das Notas")

resumo = df_filtrado["nota_media_5_notas"].describe().to_frame().T
resumo = resumo.rename(columns={
    "count": "Contagem",
    "mean":  "Média",
    "std":   "Desvio Padrão",
    "min":   "Mínimo",
    "25%":   "Q1 (25%)",
    "50%":   "Mediana",
    "75%":   "Q3 (75%)",
    "max":   "Máximo",
})
resumo = resumo.round(2)

st.dataframe(resumo, use_container_width=True)
