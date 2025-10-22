# =============================================================
# 🌿 BiodivInsights - Dashboard Streamlit (versión final completa)
# =============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------
# 1️⃣ CONFIGURACIÓN GENERAL
# ------------------------------------------------------------
st.set_page_config(
    page_title="BiodivInsights - Análisis Global de Biodiversidad",
    layout="wide",
    page_icon="🌎",
)

st.markdown("""
<style>
body { background-color: #f5f7fa; font-family: 'Roboto', sans-serif; }
h1,h2,h3,h4 { color:#0b1e3a; }
.stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 2️⃣ CARGA DE DATOS
# ------------------------------------------------------------
DATA_PATH = "./data/especies_con_areas_protegidas.csv"
df = pd.read_csv(DATA_PATH)

# Quitar categoría "LC" y filas sin país
df = df[df["category"].astype(str).str.strip().ne("LC")]
df = df.dropna(subset=["COUNTRY"])

# Limpieza general
for col in ["category", "grupo", "COUNTRY", "CONTINENT", "ISO3", "IUCN_CAT"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

df["in_protected_area"] = ~df.get("WDPAID", pd.Series([np.nan] * len(df))).isna()

# Columnas climáticas por década
clim_cols = [c for c in df.columns if c.startswith("temp_avg_") and c.split("_")[-1].isdigit()]
long_clim = (
    df[["ISO3", "COUNTRY", "CONTINENT", "category", "grupo", "SHAPE_Area", "IUCN_CAT", "in_protected_area"] + clim_cols]
    .melt(
        id_vars=["ISO3", "COUNTRY", "CONTINENT", "category", "grupo", "SHAPE_Area", "IUCN_CAT", "in_protected_area"],
        value_vars=clim_cols,
        var_name="decade_col",
        value_name="temp_dev"
    )
    .assign(decade=lambda d: pd.to_numeric(
        d["decade_col"].str.extract(r"(\d{4})")[0],
        errors="coerce"
    ))
    .drop(columns="decade_col")
)
long_clim = long_clim.dropna(subset=["decade"])

# ------------------------------------------------------------
# 3️⃣ BARRA LATERAL (FILTROS)
# ------------------------------------------------------------
st.sidebar.header("🌿 Filtros Globales")

continent_filter = st.sidebar.multiselect(
    "🌍 Continente",
    sorted(df["CONTINENT"].dropna().unique())
)
category_filter = st.sidebar.multiselect(
    "🐾 Categoría IUCN",
    sorted(df["category"].dropna().unique())
)
group_filter = st.sidebar.multiselect(
    "🧬 Grupo taxonómico",
    sorted(df["grupo"].dropna().unique())
)
country_filter = st.sidebar.multiselect(
    "🏳️ País",
    sorted(df["COUNTRY"].dropna().unique())
)

st.sidebar.divider()

# Filtrar datos
filtered_df = df.copy()
if continent_filter:
    filtered_df = filtered_df[filtered_df["CONTINENT"].isin(continent_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df["category"].isin(category_filter)]
if group_filter:
    filtered_df = filtered_df[filtered_df["grupo"].isin(group_filter)]
if country_filter:
    filtered_df = filtered_df[filtered_df["COUNTRY"].isin(country_filter)]

# Descargar dataset filtrado
buffer = io.BytesIO()
filtered_df.to_csv(buffer, index=False)
buffer.seek(0)
st.sidebar.download_button(
    label="⬇️ Descargar datos filtrados",
    data=buffer,
    file_name="biodiv_filtered.csv",
    mime="text/csv"
)

st.sidebar.divider()
st.sidebar.markdown("**Autores:** Nicolás Peña Irurita, María, José Alfredo González")
st.sidebar.markdown("_Proyecto: Análisis geoespacial de biodiversidad_")

if filtered_df.empty:
    st.warning("⚠️ No hay datos disponibles con los filtros actuales.")
    st.stop()

# ------------------------------------------------------------
# 4️⃣ PESTAÑAS PRINCIPALES
# ------------------------------------------------------------
tabs = st.tabs([
    "🗺️ Mapas Globales",
    "🌍 Biodiversidad Global",
    "🧬 Taxonomía",
    "🔥 Temperatura y Clima",
    "🏞️ Áreas Protegidas",
    "📊 Análisis por País"
])

# ============================================================
# 🗺️ 1. MAPAS GLOBALES
# ============================================================
with tabs[0]:
    st.header("🗺️ Mapas Globales")

    if {"latitude", "longitude", "category"}.issubset(filtered_df.columns):
        map_df = filtered_df.dropna(subset=["latitude", "longitude", "category"])
        if len(map_df) > 40000:
            map_df = map_df.sample(40000, random_state=42)

        fig_map = px.scatter_geo(
            map_df,
            lat="latitude",
            lon="longitude",
            color="category",
            title="Mapa global de ocurrencias por categoría IUCN",
            projection="natural earth",
            opacity=0.6
        )
        st.plotly_chart(fig_map, use_container_width=True, key="map_global")

    if {"ISO3", "temp_ref_avg"}.issubset(filtered_df.columns):
        iso_temp = filtered_df.groupby(["ISO3"], as_index=False)["temp_ref_avg"].mean()
        fig11 = px.choropleth(
            iso_temp,
            locations="ISO3",
            color="temp_ref_avg",
            color_continuous_scale="RdBu_r",
            title="ΔTemp ref promedio por país"
        )
        st.plotly_chart(fig11, use_container_width=True, key="choropleth_temp")

# ============================================================
# 🌍 2. BIODIVERSIDAD GLOBAL
# ============================================================
with tabs[1]:
    st.header("🌍 Biodiversidad Global")
    c1, c2 = st.columns(2)

    if "category" in filtered_df.columns:
        fig1 = px.bar(filtered_df, x="category", color="category", title="Recuento global por categoría IUCN")
        c1.plotly_chart(fig1, use_container_width=True, key="bar_category")

    if {"grupo", "category"}.issubset(filtered_df.columns):
        grp_cat = filtered_df.groupby(["grupo", "category"], as_index=False).size()
        fig2 = px.bar(grp_cat, x="grupo", y="size", color="category",
                      barmode="stack", title="Grupo taxonómico × Categoría IUCN")
        c2.plotly_chart(fig2, use_container_width=True, key="bar_group_cat")

# ============================================================
# 🧬 3. TAXONOMÍA
# ============================================================
with tabs[2]:
    st.header("🧬 Estructura Taxonómica")

    tax_cols = [c for c in ["kingdom", "class", "order_name"] if c in filtered_df.columns]
    if len(tax_cols) >= 2:
        tax = filtered_df.groupby(tax_cols, as_index=False).size()
        fig13 = px.sunburst(tax, path=tax_cols, values="size",
                            title="Sunburst taxonómico (kingdom → class → order)")
        st.plotly_chart(fig13, use_container_width=True, key="sunburst_tax")

    if {"grupo", "category", "CONTINENT"}.issubset(filtered_df.columns):
        samp = filtered_df[["grupo", "category", "CONTINENT"]].dropna().sample(
            n=min(3000, len(filtered_df)), random_state=42)
        dims = [go.parcats.Dimension(values=samp[c], label=c) for c in ["grupo", "category", "CONTINENT"]]
        fig14 = go.Figure(data=[go.Parcats(dimensions=dims, line={"shape": "hspline"})])
        fig14.update_layout(title="Parallel Categories: grupo → categoría → continente")
        st.plotly_chart(fig14, use_container_width=True, key="parallel_tax")

# ============================================================
# 🔥 4. TEMPERATURA Y CLIMA
# ============================================================
with tabs[3]:
    st.header("🔥 Temperatura y Clima")

    if {"temp_ref_avg", "category"}.issubset(filtered_df.columns):
        fig4 = px.box(filtered_df, x="category", y="temp_ref_avg", points="outliers",
                      title="Distribución ΔTemp ref por categoría IUCN")
        st.plotly_chart(fig4, use_container_width=True, key="box_temp_cat")

    if len(clim_cols) > 0 and "temp_dev" in long_clim.columns:
        ts_global = long_clim.groupby("decade", as_index=False)["temp_dev"].mean()
        fig8 = px.line(ts_global, x="decade", y="temp_dev", markers=True,
                       title="Evolución global de ΔTemp por década")
        st.plotly_chart(fig8, use_container_width=True, key="line_temp_global")

# ============================================================
# 🏞️ 5. ÁREAS PROTEGIDAS
# ============================================================
with tabs[4]:
    st.header("🏞️ Áreas Protegidas")

    if "in_protected_area" in filtered_df.columns:
        pa_bin = filtered_df["in_protected_area"].value_counts().rename(
            {True: "En AP", False: "Fuera AP"}).reset_index()
        pa_bin.columns = ["status", "count"]
        fig15a = px.bar(pa_bin, x="status", y="count",
                        title="Especies en Áreas Protegidas vs Fuera")
        st.plotly_chart(fig15a, use_container_width=True, key="bar_pa")

# ============================================================
# 📊 6. ANÁLISIS POR PAÍS
# ============================================================
with tabs[5]:
    st.header("📊 Análisis por País")

    if "COUNTRY" in filtered_df.columns:
        top_countries = (
            filtered_df.groupby("COUNTRY")["sci_name"]
            .nunique()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        fig_top = px.bar(
            top_countries, y="COUNTRY", x="sci_name", orientation="h",
            color="sci_name", color_continuous_scale="Reds",
            title="Top 15 países con mayor número de especies en peligro"
        )
        st.plotly_chart(fig_top, use_container_width=True, key="top_countries")

        st.markdown("### 📈 Distribución de categorías por país")
        by_country = filtered_df.groupby(["COUNTRY", "category"], as_index=False).size()
        fig_country_cat = px.bar(
            by_country, x="COUNTRY", y="size", color="category", barmode="stack",
            title="Especies amenazadas por país y categoría IUCN"
        )
        st.plotly_chart(fig_country_cat, use_container_width=True, key="country_category")

