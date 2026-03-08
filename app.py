from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Analisis de Oficios", layout="wide")
st.title("Dashboard de Analisis de Oficios")

DATE_COLUMNS = [
    "FECHA_OFICIO",
    "FECHA_RECEPCION",
    "FECHA_VENCIMIENTO",
    "FECHA_RESPUESTA",
]
NUMERIC_COLUMNS = ["ALERTA", "PLAZO_DIAS_HABILES_BANCARIOS"]


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, delimiter=";")

    object_columns = df.select_dtypes(include=["object"]).columns
    for col in object_columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d-%m-%Y", errors="coerce")

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def plot_count_bar(
    series: pd.Series, title: str, xlabel: str, ylabel: str = "Cantidad"
) -> None:
    plot_df = series.reset_index()
    plot_df.columns = [xlabel, "Cantidad"]
    fig = px.bar(
        plot_df,
        x=xlabel,
        y="Cantidad",
        title=title,
        labels={xlabel: xlabel, "Cantidad": ylabel},
        color_discrete_sequence=["#3A7CA5"],
    )
    fig.update_traces(
        hovertemplate=f"{xlabel}: %{{x}}<br>Cantidad: %{{y}}<extra></extra>"
    )
    fig.update_layout(xaxis_tickangle=-30, height=380)
    st.plotly_chart(fig, use_container_width=True)


def plot_horizontal_bar(
    series: pd.Series, title: str, xlabel: str, ylabel: str
) -> None:
    plot_df = series.sort_values().reset_index()
    plot_df.columns = [ylabel, "Cantidad"]
    fig = px.bar(
        plot_df,
        x="Cantidad",
        y=ylabel,
        orientation="h",
        title=title,
        labels={"Cantidad": xlabel, ylabel: ylabel},
        color_discrete_sequence=["#2A9D8F"],
    )
    fig.update_traces(
        hovertemplate=f"{ylabel}: %{{y}}<br>Cantidad: %{{x}}<extra></extra>"
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)


def plot_histogram(series: pd.Series, title: str, xlabel: str) -> None:
    fig = px.histogram(
        series.dropna().to_frame(name=xlabel),
        x=xlabel,
        nbins=15,
        title=title,
        color_discrete_sequence=["#E76F51"],
    )
    fig.update_traces(
        hovertemplate=f"{xlabel}: %{{x}}<br>Cantidad: %{{y}}<extra></extra>"
    )
    fig.update_layout(yaxis_title="Frecuencia", height=380)
    st.plotly_chart(fig, use_container_width=True)


def plot_time_series(series: pd.Series, title: str) -> None:
    plot_df = series.reset_index()
    plot_df.columns = ["Semana", "Cantidad"]
    fig = px.line(
        plot_df,
        x="Semana",
        y="Cantidad",
        title=title,
        markers=True,
        color_discrete_sequence=["#264653"],
    )
    fig.update_traces(
        hovertemplate="Semana: %{x|%d-%m-%Y}<br>Cantidad: %{y}<extra></extra>"
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)


try:
    data = load_data("data.csv")
except FileNotFoundError:
    st.error("No se encontro data.csv en este directorio.")
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Error al leer data.csv: {exc}")
    st.stop()

st.sidebar.header("Filtros")

filtered = data.copy()
top_n = st.sidebar.selectbox("Top N para rankings", options=[10, 15, 20], index=1)

if "FECHA_OFICIO" in filtered.columns:
    min_date = filtered["FECHA_OFICIO"].min()
    max_date = filtered["FECHA_OFICIO"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.sidebar.date_input(
            "Rango FECHA_OFICIO",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered = filtered[
                filtered["FECHA_OFICIO"].between(
                    pd.to_datetime(start_date), pd.to_datetime(end_date)
                )
            ]

for col, label in [
    ("ESTADO", "Estado"),
    ("RESPONSABLE", "Responsable"),
    ("TIPO", "Tipo"),
    ("CANAL", "Canal"),
    ("TIPO_ORGANISMO", "Tipo organismo"),
]:
    if col in filtered.columns:
        options = sorted(filtered[col].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect(label, options)
        if selected:
            filtered = filtered[filtered[col].isin(selected)]

st.subheader("Resumen")
col1, col2, col3, col4 = st.columns(4)

total = len(filtered)
cerrados = (
    int((filtered.get("ESTADO") == "CERRADO").sum())
    if "ESTADO" in filtered.columns
    else 0
)
abiertos = total - cerrados if "ESTADO" in filtered.columns else 0
alerta_prom = (
    filtered["ALERTA"].mean() if "ALERTA" in filtered.columns else float("nan")
)

if "FECHA_RESPUESTA" in filtered.columns:
    pct_respuesta = filtered["FECHA_RESPUESTA"].notna().mean() * 100 if total else 0.0
else:
    pct_respuesta = 0.0

col1.metric("Registros", f"{total}")
col2.metric("Cerrados", f"{cerrados}")
col3.metric("Abiertos", f"{abiertos}")
col4.metric("% con respuesta", f"{pct_respuesta:.1f}%")
st.caption(
    f"Alerta promedio: {alerta_prom:.2f}"
    if pd.notna(alerta_prom)
    else "Alerta promedio: N/D"
)

if filtered.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

st.subheader("Graficas")
g1, g2 = st.columns(2)
with g1:
    if "ESTADO" in filtered.columns:
        estado_counts = filtered["ESTADO"].fillna("Sin estado").value_counts()
        plot_count_bar(estado_counts, "Distribucion por Estado", "Estado")
with g2:
    if "RESPONSABLE" in filtered.columns:
        top_resp = (
            filtered["RESPONSABLE"].fillna("Sin responsable").value_counts().head(top_n)
        )
        plot_horizontal_bar(top_resp, "Top Responsables", "Cantidad", "Responsable")

g3, g4 = st.columns(2)
with g3:
    if "TIPO" in filtered.columns:
        tipo_counts = filtered["TIPO"].fillna("Sin tipo").value_counts()
        plot_count_bar(tipo_counts, "Distribucion por Tipo", "Tipo")
with g4:
    if "ALERTA" in filtered.columns:
        plot_histogram(filtered["ALERTA"], "Distribucion de ALERTA", "ALERTA")

g5, g6 = st.columns(2)
with g5:
    if "FECHA_OFICIO" in filtered.columns:
        weekly = (
            filtered.dropna(subset=["FECHA_OFICIO"])
            .set_index("FECHA_OFICIO")
            .resample("W")
            .size()
        )
        if not weekly.empty:
            plot_time_series(weekly, "Evolucion Semanal (FECHA_OFICIO)")
        else:
            st.info("Sin datos de FECHA_OFICIO para graficar.")
with g6:
    if "CANAL" in filtered.columns:
        canal_counts = filtered["CANAL"].fillna("Sin canal").value_counts()
        plot_count_bar(canal_counts, "Distribucion por Canal", "Canal")

g7, g8 = st.columns(2)
with g7:
    if "TIPO_ORGANISMO" in filtered.columns:
        organismo_counts = (
            filtered["TIPO_ORGANISMO"].fillna("Sin tipo_organismo").value_counts()
        )
        plot_count_bar(
            organismo_counts, "Distribucion por Tipo Organismo", "Tipo organismo"
        )
with g8:
    if "JUZGADO / LIQUIDADOR" in filtered.columns:
        juzgado_counts = (
            filtered["JUZGADO / LIQUIDADOR"]
            .fillna("Sin juzgado/liquidador")
            .value_counts()
            .head(top_n)
        )
        plot_horizontal_bar(
            juzgado_counts,
            "Top Juzgado / Liquidador",
            "Cantidad",
            "Juzgado / Liquidador",
        )

st.subheader("Vista tabular")
st.dataframe(filtered, use_container_width=True)
