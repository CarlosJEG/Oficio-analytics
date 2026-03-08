# Analisis de `data.csv` con Streamlit

## Requisitos
- Python 3.10+ (recomendado 3.12)

## Configuracion
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar dashboard
```bash
streamlit run app.py
```

## Que incluye
- Carga de `data.csv` con separador `;`
- Limpieza de texto y conversion de fechas (`dd-mm-YYYY`)
- Filtros por fecha, estado, responsable, tipo, canal y tipo organismo
- Selector de Top N para rankings
- Metricas generales
- Graficas interactivas con Plotly (hover con cantidad):
  - Estado
  - Top responsables
  - Tipo
  - Histograma de alerta
  - Evolucion semanal por fecha de oficio
  - Canal
  - Tipo organismo
  - Top juzgado / liquidador
