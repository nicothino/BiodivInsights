# ============================================================
# Biodiversity Nexus - Repositorio de pérdida de biodiversidad
# ============================================================
# Autor: Nicolás Peña Irurita, Maria
# Fecha: Octubre 2025
# Descripción:
# Dashboard interactivo en Shiny para explorar especies amenazadas
# por país, continente y categoría UICN con visualizaciones Plotly.
# ------------------------------------------------------------

from shiny import App, ui, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import warnings

# ------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL
# ------------------------------------------------------------

warnings.filterwarnings("ignore", category=FutureWarning)

# Cargar datos
df = pd.read_csv("./data/points_with_country_continent_safe.csv")

# Filtrar especies con categoría distinta de LC (Least Concern)
df = df[df["category"] != "LC"]

# Limpiar coordenadas y valores extremos
df = df.replace([float("inf"), float("-inf")], None)
df = df.dropna(subset=["latitude", "longitude"])

# ------------------------------------------------------------
# 2. DEFINICIÓN DE LA INTERFAZ (UI)
# ------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("BiodivInsights"),
        ui.p("Repositorio de pérdida de biodiversidad"),
        ui.hr(),
        ui.h4("Filtros de exploración"),

        ui.input_selectize(
            "continent",
            "Selecciona continente:",
            choices=sorted(df["CONTINENT"].dropna().unique().tolist()),
            multiple=True
        ),

        ui.input_selectize(
            "category",
            "Selecciona categoría UICN:",
            choices=sorted(df["category"].dropna().unique().tolist()),
            multiple=True
        ),

        ui.input_selectize(
            "class_select",
            "Selecciona clase biológica:",
            choices=sorted(df["class"].dropna().unique().tolist()),
            multiple=True
        ),

        ui.hr(),
        ui.h6("Autor: Nicolás Peña Irurita, Maria, Jose Alfredo Gonzáles"),
        ui.h6("Proyecto: Análisis geoespacial de biodiversidad"),
        width=280,
        open="open"
    ),

    ui.navset_card_tab(
        # ------------------------------------------------------------
        # Mapa global
        # ------------------------------------------------------------
        ui.nav_panel(
            "Mapa Global",
            ui.h3("Distribución geográfica de especies amenazadas"),
            output_widget("map_plot")
        ),

        # ------------------------------------------------------------
        # Países
        # ------------------------------------------------------------
        ui.nav_panel(
            "Países",
            ui.h3("Top 10 países con mayor número de especies amenazadas"),
            output_widget("country_plot")
        ),

        # ------------------------------------------------------------
        # Clases biológicas
        # ------------------------------------------------------------
        ui.nav_panel(
            "Clases Biológicas",
            ui.h3("Distribución de especies por clase biológica"),
            output_widget("class_plot")
        ),

        # ------------------------------------------------------------
        # Resumen por continente
        # ------------------------------------------------------------
        ui.nav_panel(
            "Resumen por Continente",
            ui.h3("Matriz de especies únicas por continente y categoría"),
            output_widget("heatmap_plot")
        ),
    ),
    title="Biodiversity Nexus"
)

# ------------------------------------------------------------
# 3. LÓGICA DEL SERVIDOR
# ------------------------------------------------------------
def server(input, output, session):

    # Reactive: datos filtrados según inputs
    @reactive.calc
    def filtered_df():
        data = df.copy()

        # Aplicar filtros según los inputs
        if input.continent():
            data = data[data["CONTINENT"].isin(input.continent())]
        if input.category():
            data = data[data["category"].isin(input.category())]
        if input.class_select():
            data = data[data["class"].isin(input.class_select())]

        # 🔧 LIMPIEZA CRÍTICA (soluciona el error)
        data = data.replace([float("inf"), float("-inf")], None)  # Quitar infinitos
        data = data.dropna(subset=["latitude", "longitude"])      # Quitar coordenadas faltantes
        data = data.dropna(subset=["COUNTRY", "CONTINENT", "category"], how="any")  # Quitar filas sin info esencial

        return data

    # ------------------------------------------------------------
    # Mapa Global
    # ------------------------------------------------------------
    @output
    @render_widget
    def map_plot():
        data = filtered_df().dropna(subset=["latitude", "longitude", "category"])
        fig = px.scatter_geo(
            data,
            lat="latitude",
            lon="longitude",
            color="category",
            hover_name="sci_name",
            hover_data=["COUNTRY", "CONTINENT", "class"],
            projection="natural earth",
            title="Mapa global de especies amenazadas",
            color_discrete_map={
                "CR": "#8B0000",
                "EN": "#E74C3C",
                "VU": "#F5B041",
                "NT": "#F7DC6F",
                "DD": "#7F8C8D",
                "EX": "#4A235A",
                "EW": "#6C3483",
            },
        )
        fig.update_geos(
            showcountries=True,
            showcoastlines=True,
            showland=True,
            landcolor="rgb(240, 240, 240)"
        )
        fig.update_layout(height=600, margin=dict(l=10, r=10, t=60, b=10))
        return fig

    # ------------------------------------------------------------
    # Top 10 países con más especies amenazadas
    # ------------------------------------------------------------
    @output
    @render_widget
    def country_plot():
        data = filtered_df()
        top_countries = (
            data.groupby("COUNTRY")["sci_name"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig = px.bar(
            top_countries,
            x="sci_name",
            y="COUNTRY",
            orientation="h",
            color="sci_name",
            color_continuous_scale="Reds",
            title="Top 10 países con más especies amenazadas",
            labels={"sci_name": "Número de especies únicas", "COUNTRY": "País"},
        )
        fig.update_layout(coloraxis_showscale=False, height=500, margin=dict(l=40, r=40, t=50, b=40))
        return fig

    # ------------------------------------------------------------
    # Distribución de especies por clase biológica
    # ------------------------------------------------------------
    @output
    @render_widget
    def class_plot():
        data = filtered_df()
        top_classes = data["class"].value_counts().nlargest(10).index
        fig = px.histogram(
            data[data["class"].isin(top_classes)],
            x="class",
            color="category",
            barmode="stack",
            title="Distribución de especies amenazadas por clase biológica",
            color_discrete_sequence=px.colors.sequential.Viridis,
        )
        fig.update_layout(xaxis_title="Clase", yaxis_title="Número de registros", height=500)
        return fig

    # ------------------------------------------------------------
    # Resumen por continente y categoría (heatmap)
    # ------------------------------------------------------------
    @output
    @render_widget
    def heatmap_plot():
        data = filtered_df()
        heat_df = (
            data.groupby(["CONTINENT", "category"])["sci_name"]
            .nunique()
            .reset_index()
            .pivot(index="CONTINENT", columns="category", values="sci_name")
            .fillna(0)
        )
        fig = px.imshow(
            heat_df,
            color_continuous_scale="Reds",
            title="Matriz de especies únicas por continente y categoría UICN",
            labels=dict(x="Categoría", y="Continente", color="Número de especies"),
        )
        fig.update_layout(height=500, margin=dict(l=40, r=40, t=50, b=40))
        return fig


# ------------------------------------------------------------
# 4. EJECUCIÓN DE LA APLICACIÓN
# ------------------------------------------------------------
app = App(app_ui, server)
