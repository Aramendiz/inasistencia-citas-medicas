# Predicción y caracterización de la inasistencia a citas médicas de consulta externa

Proyecto Integrador de Ciencia de Datos e Inteligencia Artificial
Maestría en Inteligencia Artificial, Universidad de La Salle (Bogotá, Colombia)
Autor: Jairo Teófilo Araméndiz Pinzón · Docente: Fabián Camilo Castro Riveros

**Tablero en vivo:** _pegar aquí la URL de Streamlit Community Cloud_

## Descripción

A partir de 110.527 citas de consulta externa de la red pública de salud de Vitória (Brasil, 2016), el proyecto:

- predice la probabilidad de que un paciente no asista a su cita (clasificación);
- estima los días de espera entre el agendamiento y la cita (regresión);
- segmenta a los pacientes según su patrón de uso del servicio (clustering);
- presenta los resultados en un tablero interactivo con predicción en vivo.

El trabajo se conecta con el proyecto de grado *AgendamientoIA*, un sistema conversacional de agendamiento médico por WhatsApp que envía recordatorios automáticos: el modelo de inasistencia sirve para decidir a qué pacientes priorizar.

## Resultados principales (conjunto de prueba)

| Tarea | Mejor modelo | Métricas |
|---|---|---|
| Clasificación de la inasistencia | XGBoost | AUC-ROC 0,740 · F1 0,455 · Recall 0,770 |
| Regresión de los días de espera | XGBoost Regressor | R² 0,138 · RMSE 14,07 · MAE 10,05 |
| Segmentación de pacientes | K-Means (K = 5) | Silueta 0,349 |

## Estructura del repositorio

```
├── data/                 KaggleV2-May-2016.csv (dataset original)
├── notebooks/
│   ├── Entregable1_EDA.ipynb               Fase 1: planteamiento y análisis exploratorio
│   ├── Entregable2_Preprocesamiento.ipynb  Fase 2: limpieza, variables, partición y baseline
│   └── Entregable3_Modelado.ipynb          Fase 3: modelos, MLP, optimización, SHAP y clustering
├── src/pipeline.py       Limpieza, variables, partición y entrenamiento reutilizables
├── dashboard/
│   ├── app.py            Tablero Streamlit
│   └── requirements.txt  Dependencias del tablero (las usa Streamlit Cloud)
├── figs/                 Figuras del análisis exploratorio
├── informe/              Informes en PDF
└── requirements.txt      Versiones exactas usadas en los cuadernos
```

## Cómo reproducir

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Cuadernos (ejecutar desde la carpeta notebooks/, en orden)
jupyter notebook notebooks/

# Tablero
streamlit run dashboard/app.py
```

El tablero entrena los modelos al iniciar, con los hiperparámetros elegidos en la Fase 3, y los guarda en caché. La primera carga tarda alrededor de un minuto.

## Datos

*Medical Appointment No Shows*, publicado por Joni Hoppen en Kaggle: <https://www.kaggle.com/datasets/joniarroba/noshowappointments>. Licencia CC BY-NC-SA 4.0. Se redistribuye aquí sin modificaciones y con fines académicos no comerciales.
