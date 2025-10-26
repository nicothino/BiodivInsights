#  BiodivInsights  
### Plataforma Global de Monitoreo y Predicción de Biodiversidad mediante Inteligencia Artificial  

**Autores:** Nicolás Peña Irurita, Maria, Jose Alfredo Gonzáles  
**Correos:** nicolas.pena_irurita@uao.edu.co , marna_de.valencia@uao.edu.co, jose_alf.gonzalias@uao.edu.co 
<center>
<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/94bb032e-bbd0-4ae6-bdaa-80dbd50f553f" />
<center>
---

##  Descripción General

**BiodivInsights** es una plataforma de código abierto diseñada para integrar, analizar y visualizar datos ambientales y biológicos con el fin de apoyar el seguimiento del **Objetivo de Desarrollo Sostenible 15 (ODS 15: Vida de ecosistemas terrestres)**.

El proyecto unifica múltiples fuentes de datos sobre biodiversidad, áreas protegidas y cambio climático, aplicando **Inteligencia Artificial**, análisis geoespacial y visualización interactiva para generar información accesible, actualizada y útil para investigadores, gobiernos y organizaciones ambientales.

El resultado final es un **dashboard interactivo (`dashboard.py`)** que muestra patrones, tendencias y predicciones globales sobre biodiversidad y cambio ambiental.

---

## Estructura del Repositorio

📁 BiodivInsights/

```bash
├── data/
│ ├── biodiversidad_centroides.csv
│ ├── simplified_polygons.csv
│ ├── gadm_410.gpkg
│ ├── areas_protegidas.csv
│ └── temperatura_superficie.csv
│
├── notebooks/
│ ├── eda_especies_en_peligro.ipynb
│ ├── eda_areas_protegidas.ipynb
│ ├── eda_cambio_temperatura.ipynb
│ └── merge_biodiversidad_global.ipynb
│
├── dashboard.py
├── requirements.txt
└── README.md

```

---

## Es importante saber el nivel de amenaza para loas especies

Estas son las **categorías oficiales de amenaza** de la *Lista Roja de la UICN* (Unión Internacional para la Conservación de la Naturaleza).  
Indican el nivel de riesgo de extinción de cada especie.

| Código | Categoría en inglés | Descripción |
|:-------|:--------------------|:-------------|
| **EX** | Extinct | Extinto. No queda ningún individuo conocido. |
| **EW** | Extinct in the Wild | Extinto en estado silvestre (solo sobreviven en cautiverio o cultivo). |
| **CR** | Critically Endangered | En peligro crítico: riesgo extremadamente alto de extinción en estado silvestre. |
| **EN** | Endangered | En peligro: riesgo muy alto de extinción. |
| **VU** | Vulnerable | Vulnerable: riesgo alto de extinción. |
| **NT** | Near Threatened | Casi amenazado: podría calificar en el futuro cercano como amenazado. |
| **LC** | Least Concern | Preocupación menor: riesgo bajo de extinción; especie común o abundante. |
| **DD** | Data Deficient | Datos insuficientes: no hay suficiente información para evaluar el riesgo. |

<img width="1417" height="656" alt="image" src="https://github.com/user-attachments/assets/990cf220-7d01-413a-8f7e-77517ea0eca8" />

##  Metodología General

### 1️ EDA de Especies en Peligro (`eda_especies_en_peligro.ipynb`)

- Se integraron datasets de mamíferos, anfibios, reptiles y plantas de la **[IUCN Red List](https://www.iucnredlist.org/)**.  
- Se unificaron todos los registros en un único CSV con columnas `latitude`, `longitude` y `species`.  
- Se optimizó el tamaño mediante exportación a CSV simplificado.  

#### Objetivo:
Asociar cada especie con el país y continente correspondiente usando análisis espacial.

#### Proceso técnico:
- GeoDataFrame de polígonos (`gadm_410.gpkg`) → columnas `COUNTRY`, `CONTINENT`, `geometry`.  
- GeoDataFrame de puntos (`biodiversidad_centroides.csv`).  
- **Spatial Join (GeoPandas):** unión espacial entre puntos y polígonos.  
- Exportación del resultado con país y continente.  

> **Nota:** Se reemplazó el uso de `Dask-GeoPandas` por `GeoPandas` puro con procesamiento por bloques (5.000 registros) para evitar fallos de memoria.

---

### 2️ EDA de Áreas Protegidas (`eda_areas_protegidas.ipynb`)

**Fuente:** [Protected Planet](https://www.protectedplanet.net/en/search-areas?geo_type=country)
<img width="1074" height="548" alt="image" src="https://github.com/user-attachments/assets/7f71828b-57d7-4338-9254-c8e9d2e99772" />

#### Objetivo:
Analizar la distribución de áreas protegidas por año y entidad responsable.

#### Principales resultados:
- Años con más áreas declaradas: **2014** y **2018**.  
- Entidades líderes: **Ministerio del Medio Ambiente de Japón** y **UNESCO-MAB**.  

####  Visualizaciones:
- Número de áreas protegidas por año de creación.  
- Áreas protegidas por entidad responsable.  


---

### 3️ EDA Climático-Sanitario (`eda_cambio_temperatura.ipynb`)

**Fuente:** [IMF Climate Data](https://climatedata.imf.org/datasets/4063314923d74187be9596f10d034914/explore)

####  Datos:
- **Años:** 1961–2024  
- **Variables:** temperatura media, precipitación, eventos climáticos (El Niño / La Niña), casos de dengue, eventos extremos.  

####  Hallazgos:
- Temperatura media global: **14.5°C**  
- Correlación positiva entre temperatura y casos de **dengue**.  
- Relación directa entre lluvias y eventos extremos.  
- Identificación de **56 eventos El Niño** y **73 La Niña**.  

---

### 4️ Integración de Datos Globales (`merge_biodiversidad_global.ipynb`)

Se unificaron los resultados anteriores para construir una base de datos única de biodiversidad, áreas protegidas y variables climáticas por país y año.  
Esto permite alimentar el **dashboard interactivo** y generar análisis correlativos entre biodiversidad, cambio climático y conservación.

---

##  Dashboard Interactivo (`dashboard.py`)

Aplicación construida en **Streamlit** que muestra:

- 🌿 Mapa mundial de biodiversidad por especies amenazadas.  
- 🏞️ Análisis temporal de áreas protegidas.  
- 🌡️ Indicadores climáticos y correlaciones con salud.  
- 🔮 Predicciones de pérdida de biodiversidad por región.  

El dashboard integra resultados en línea con los **indicadores del ODS 15**, entre ellos:

| Meta ODS 15 | Indicador | Descripción |
|--------------|------------|--------------|
| **15.1.1** | Superficie forestal (%) | Proporción de superficie cubierta por bosques. |
| **15.1.2** | Lugares importantes para la biodiversidad en zonas protegidas | Cobertura de ecosistemas críticos bajo protección. |
| **15.2.1** | Avances hacia la gestión forestal sostenible | Seguimiento de deforestación y reforestación. |
| **15.3.1** | Tierras degradadas (%) | Identificación de zonas con desertificación o pérdida de suelo. |
| **15.4.1** | Biodiversidad en ecosistemas montañosos | Cobertura verde e índices de conservación. |
| **15.5.1** | Índice de la Lista Roja | Estado de conservación global de especies. |
| **15.7.1** | Caza furtiva y tráfico ilegal | Detección de presiones sobre fauna silvestre. |

---

##  Tecnologías Utilizadas

| Categoría | Herramientas |
|------------|--------------|
| Lenguaje | Python 3.11 |
| Librerías | GeoPandas, Pandas, Shapely, Matplotlib, Seaborn, Streamlit |
| Procesamiento Espacial | PostGIS / GeoPackage / WKT |
| Análisis Climático | Prophet, Scikit-learn |
| Visualización | Matplotlib, Folium, Streamlit |
| Infraestructura | AWS / GitHub / Datos abiertos |

---

##  Instalación

```bash
git clone https://github.com/nicothino/BiodivInsights.git
cd BiodivInsights
pip install -r requirements.txt
streamlit run app.py
```
## Resultados Esperados

🌍 Dashboard interactivo global.

🔗 Correlaciones entre variables ambientales, sanitarias y de biodiversidad.

📈 Dataset consolidado con proyecciones futuras.

🧩 Base técnica para reportar indicadores del ODS 15.

## Contribuciones

Este proyecto es de código abierto y busca fomentar la colaboración científica y técnica.
Puedes contribuir mediante:

Nuevas fuentes de datos (ODS 13, ODS 14).

Modelos predictivos de deforestación o riesgo de especies.

Mejoras en el dashboard.
