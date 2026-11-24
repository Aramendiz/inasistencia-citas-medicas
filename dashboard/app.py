"""Tablero interactivo — Predicción y caracterización de la inasistencia a citas médicas.

Proyecto Integrador de Ciencia de Datos, Maestría en Inteligencia Artificial, Universidad de La Salle.
Autor: Jairo Teófilo Araméndiz Pinzón.

Ejecución local:  streamlit run dashboard/app.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import (f1_score, precision_score, r2_score, recall_score, roc_auc_score,
                             mean_absolute_error, mean_squared_error)

warnings.filterwarnings('ignore')
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
import pipeline as P  # noqa: E402

st.set_page_config(page_title='Inasistencia a citas médicas', layout='wide')

AZUL, ROJO, GRIS = '#2f6db5', '#d1495b', '#8a8f98'
COLORES_SEG = {'Espera larga, no asistieron': '#d1495b', 'Espera larga con SMS, asistieron': '#2f6db5',
               'Citas cercanas, asistieron': '#3a9d6a', 'Usuarios frecuentes': '#e39b2d',
               'Adultos mayores con condiciones crónicas': '#7b5ea7'}
DIAS_ORDEN = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']


# ------------------------------------------------------------------ datos y modelos (se calculan una sola vez)
@st.cache_resource(show_spinner='Preparando datos y entrenando los modelos (solo la primera vez, ~1 minuto)...')
def cargar_todo():
    df = P.particionar(P.cargar_y_preparar(P.buscar_csv(RAIZ / 'data')))
    ent, val, pru = (df[df.conjunto == c] for c in ['entrenamiento', 'validacion', 'prueba'])

    clf = P.entrenar_clasificador(ent)
    umbral = P.umbral_f1(val.inasistencia, clf.predict_proba(val)[:, 1])
    p_pru = clf.predict_proba(pru)[:, 1]
    pred = (p_pru >= umbral).astype(int)
    met_clf = {'AUC-ROC': roc_auc_score(pru.inasistencia, p_pru), 'F1': f1_score(pru.inasistencia, pred),
               'Recall': recall_score(pru.inasistencia, pred), 'Precisión': precision_score(pru.inasistencia, pred)}

    reg = P.entrenar_regresor(ent)
    r_pru = reg.predict(pru)
    met_reg = {'R²': r2_score(pru.dias_espera, r_pru), 'RMSE': mean_squared_error(pru.dias_espera, r_pru) ** 0.5,
               'MAE': mean_absolute_error(pru.dias_espera, r_pru)}

    m = clf.named_steps['m']
    imp = pd.Series(m.get_booster().get_score(importance_type='gain'))
    nombres = clf.named_steps['prep'].get_feature_names_out()
    imp.index = [nombres[int(k[1:])] if k.startswith('f') and k[1:].isdigit() else k for k in imp.index]
    imp = (imp / imp.sum()).sort_values(ascending=False)

    pac = P.tabla_pacientes(df)
    esc, km, pca, X = P.entrenar_clustering(pac)
    pac['segmento_id'] = km.labels_
    xy = pca.transform(X)
    pac['pc1'], pac['pc2'] = xy[:, 0], xy[:, 1]
    nombres_seg = nombrar_segmentos(pac)
    pac['segmento'] = pac.segmento_id.map(nombres_seg)
    df = df.merge(pac[['segmento']], left_on='id_paciente', right_index=True, how='left')

    barrios = df.groupby('barrio').size().sort_values(ascending=False).index.tolist()
    return df, clf, umbral, met_clf, reg, met_reg, imp, pac, pca.explained_variance_ratio_.sum(), barrios


def nombrar_segmentos(pac):
    """Asigna nombres a los clústeres según su perfil (no según el número, que puede cambiar entre versiones)."""
    perf = pac.groupby('segmento_id')[['edad', 'n_citas', 'tasa_inasistencia', 'espera_media', 'prop_sms']].mean()
    nombres, libres = {}, list(perf.index)
    def tomar(serie, nombre):
        i = serie.loc[libres].idxmax(); nombres[i] = nombre; libres.remove(i)
    tomar(perf.tasa_inasistencia, 'Espera larga, no asistieron')
    tomar(perf.edad, 'Adultos mayores con condiciones crónicas')
    tomar(perf.n_citas, 'Usuarios frecuentes')
    tomar(perf.prop_sms, 'Espera larga con SMS, asistieron')
    for i in libres:
        nombres[i] = 'Citas cercanas, asistieron'
    return nombres


df, clf, UMBRAL, MET_CLF, reg, MET_REG, IMP, pac, VAR_PCA, BARRIOS = cargar_todo()

# ------------------------------------------------------------------ encabezado
st.title('Inasistencia a citas médicas de consulta externa')
st.caption('Proyecto Integrador de Ciencia de Datos · Maestría en Inteligencia Artificial, Universidad de La Salle · '
           'Jairo Teófilo Araméndiz Pinzón · Datos: Medical Appointment No Shows (Kaggle, CC BY-NC-SA 4.0), '
           f'{len(df):,} citas en Vitória, Brasil, 2016'.replace(',', '.'))

# ------------------------------------------------------------------ filtros
with st.sidebar:
    st.header('Filtros')
    fmin, fmax = df.fecha_cita.min().date(), df.fecha_cita.max().date()
    rango = st.date_input('Fecha de la cita', (fmin, fmax), min_value=fmin, max_value=fmax)
    sexo = st.multiselect('Sexo', ['F', 'M'], default=['F', 'M'], format_func=lambda s: 'Femenino' if s == 'F' else 'Masculino')
    edades = st.slider('Edad (años)', 0, 110, (0, 110))
    espera = st.slider('Días de espera', 0, int(df.dias_espera.max()), (0, int(df.dias_espera.max())))
    sms = st.radio('Recordatorio SMS', ['Todos', 'Con SMS', 'Sin SMS'], horizontal=True)
    barrios_sel = st.multiselect('Barrio', BARRIOS, placeholder='Todos los barrios')
    segmentos_sel = st.multiselect('Segmento de paciente', sorted(pac.segmento.unique()), placeholder='Todos los segmentos')

f = df[(df.fecha_cita.dt.date >= rango[0]) & (df.fecha_cita.dt.date <= (rango[1] if len(rango) > 1 else rango[0]))
       & df.sexo.isin(sexo) & df.dias_espera.between(*espera)
       & (df.edad.between(*edades) | df.edad.isna())]
if sms != 'Todos':
    f = f[f.sms_recibido == (1 if sms == 'Con SMS' else 0)]
if barrios_sel:
    f = f[f.barrio.isin(barrios_sel)]
if segmentos_sel:
    f = f[f.segmento.isin(segmentos_sel)]

if f.empty:
    st.warning('Ningún registro cumple los filtros seleccionados.')
    st.stop()


def fmt(x, d=1):
    return f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


# ------------------------------------------------------------------ tarjetas KPI
k = st.columns(5)
k[0].metric('Citas', fmt(len(f), 0)); k[0].caption(f'{fmt(f.id_paciente.nunique(), 0)} pacientes')
k[1].metric('Tasa de inasistencia', f'{fmt(f.inasistencia.mean() * 100)} %',
            f'{fmt((f.inasistencia.mean() - df.inasistencia.mean()) * 100)} pp frente al total', delta_color='inverse')
k[2].metric('Espera media', f'{fmt(f.dias_espera.mean())} días'); k[2].caption(f'Mediana: {fmt(f.dias_espera.median(), 0)} días')
k[3].metric('Citas con SMS', f'{fmt(f.sms_recibido.mean() * 100)} %')
k[4].metric('AUC-ROC (prueba)', fmt(MET_CLF['AUC-ROC'], 3)); k[4].caption(f"El modelo detecta el {fmt(MET_CLF['Recall'] * 100, 0)} % de las inasistencias")

tab1, tab2, tab3, tab4 = st.tabs(['Panorama', 'Predicción en vivo', 'Segmentación de pacientes', 'Desempeño de los modelos'])

# ------------------------------------------------------------------ 1. panorama
with tab1:
    c1, c2 = st.columns(2)
    tramos = pd.cut(f.dias_espera, [-1, 0, 7, 15, 30, 60, 200], labels=['Mismo día', '1-7', '8-15', '16-30', '31-60', '>60'])
    t = f.groupby(tramos, observed=True).agg(tasa=('inasistencia', 'mean'), citas=('id_cita', 'count')).reset_index()
    fig = px.bar(t, x='dias_espera', y=t.tasa * 100, text=(t.tasa * 100).round(1), color_discrete_sequence=[AZUL],
                 labels={'dias_espera': 'Días de espera', 'y': '% inasistencia'}, hover_data={'citas': True})
    fig.update_layout(title='Inasistencia según los días de espera', height=360, margin=dict(t=50, b=10))
    c1.plotly_chart(fig, use_container_width=True)

    t2 = f[f.dias_espera > 0].assign(tramo=tramos).groupby(['tramo', 'sms_recibido'], observed=True).inasistencia.mean().reset_index()
    t2['SMS'] = t2.sms_recibido.map({0: 'Sin SMS', 1: 'Con SMS'})
    fig = px.bar(t2, x='tramo', y=t2.inasistencia * 100, color='SMS', barmode='group', color_discrete_map={'Sin SMS': GRIS, 'Con SMS': AZUL},
                 labels={'tramo': 'Días de espera', 'y': '% inasistencia'})
    fig.update_layout(title='Efecto del SMS comparando citas con la misma espera', height=360, margin=dict(t=50, b=10))
    c2.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    d = f.groupby(f.fecha_cita.dt.date).agg(citas=('id_cita', 'count'), tasa=('inasistencia', 'mean')).reset_index()
    fig = go.Figure()
    fig.add_bar(x=d.fecha_cita, y=d.citas, name='Citas', marker_color='#c9d6e8', yaxis='y')
    fig.add_scatter(x=d.fecha_cita, y=d.tasa * 100, name='% inasistencia', line=dict(color=ROJO), yaxis='y2')
    fig.update_layout(title='Citas e inasistencia por día', height=360, margin=dict(t=50, b=10),
                      yaxis=dict(title='Citas'), yaxis2=dict(title='% inasistencia', overlaying='y', side='right'),
                      legend=dict(orientation='h', y=-0.2))
    c3.plotly_chart(fig, use_container_width=True)

    e = f.groupby('grupo_etario').inasistencia.mean().reindex(P.GRUPOS_EDAD[1]).reset_index()
    fig = px.bar(e, x='grupo_etario', y=e.inasistencia * 100, text=(e.inasistencia * 100).round(1), color_discrete_sequence=[AZUL],
                 labels={'grupo_etario': 'Grupo de edad', 'y': '% inasistencia'})
    fig.update_layout(title='Inasistencia por grupo de edad', height=360, margin=dict(t=50, b=10))
    c4.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------ 2. predicción en vivo
with tab2:
    st.subheader('Riesgo de inasistencia de una nueva cita')
    st.write('Ingrese los datos de la cita. El modelo XGBoost entrenado en la Fase 3 estima la probabilidad de que el paciente '
             'no asista, y el regresor estima la espera típica para un paciente con ese perfil.')
    with st.form('prediccion'):
        a, b, c = st.columns(3)
        edad = a.number_input('Edad', 0, 110, 35)
        sexo_in = a.selectbox('Sexo', ['F', 'M'], format_func=lambda s: 'Femenino' if s == 'F' else 'Masculino')
        barrio = a.selectbox('Barrio', BARRIOS)
        dias_espera = b.number_input('Días entre el agendamiento y la cita', 0, 180, 10)
        dia_agenda = b.selectbox('Día en que se agenda', DIAS_ORDEN[:5])
        hora = b.slider('Hora en que se agenda', 6, 21, 9)
        sms_in = b.checkbox('Recibe recordatorio SMS', value=dias_espera >= 3)
        cron = c.multiselect('Condiciones', ['Hipertensión', 'Diabetes', 'Alcoholismo'], placeholder='Ninguna')
        bolsa = c.checkbox('Beneficiario de Bolsa Família')
        disc = c.selectbox('Discapacidades registradas', [0, 1, 2, 3, 4])
        previas = c.number_input('Citas anteriores del paciente', 0, 50, 0)
        ina_prev = c.number_input('Inasistencias anteriores', 0, 50, 0)
        enviar = st.form_submit_button('Calcular riesgo', type='primary')

    ina_prev = min(ina_prev, previas)
    semana = list(P.DIAS.values())
    dia_cita = semana[(semana.index(dia_agenda) + dias_espera) % 7]   # el día de la cita se deduce de la espera
    fila = pd.DataFrame([{
        'edad': float(edad), 'dias_espera': dias_espera, 'hora_agendamiento': hora, 'citas_previas': previas,
        'inasistencias_previas': ina_prev, 'citas_mismo_dia': 1,
        'tasa_inasistencia_previa': ina_prev / previas if previas else np.nan,
        'sexo_f': int(sexo_in == 'F'), 'bolsa_familia': int(bolsa), 'hipertension': int('Hipertensión' in cron),
        'diabetes': int('Diabetes' in cron), 'alcoholismo': int('Alcoholismo' in cron), 'discapacidad': disc,
        'sms_recibido': int(sms_in), 'cita_mismo_dia': int(dias_espera == 0), 'n_condiciones_cronicas': len(cron),
        'dia_semana_cita': dia_cita, 'dia_semana_agendamiento': dia_agenda,
        'grupo_etario': P.grupo_etario(pd.Series([float(edad)])).iloc[0], 'barrio': barrio}])
    prob = float(clf.predict_proba(fila)[:, 1][0])
    espera_est = max(0.0, float(reg.predict(fila)[0]))

    if prob < UMBRAL:
        nivel, color, accion = 'Bajo', '#3a9d6a', 'Recordatorio estándar 24 horas antes.'
    elif prob < 0.65:
        nivel, color, accion = 'Medio', '#e39b2d', 'Recordatorio con solicitud de confirmación (CONFIRMAR / CANCELAR).'
    else:
        nivel, color, accion = 'Alto', ROJO, ('Confirmación activa y, si la espera es larga, ofrecer una fecha más cercana '
                                              'o liberar el cupo para lista de espera.')
    r1, r2 = st.columns([1, 1.3])
    gauge = go.Figure(go.Indicator(mode='gauge+number', value=prob * 100, number={'suffix': ' %'},
                                   gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color},
                                          'steps': [{'range': [0, UMBRAL * 100], 'color': '#e3f1e8'},
                                                    {'range': [UMBRAL * 100, 65], 'color': '#fbefd9'},
                                                    {'range': [65, 100], 'color': '#f8dde1'}]},
                                   title={'text': 'Probabilidad estimada de inasistencia'}))
    gauge.update_layout(height=300, margin=dict(t=60, b=10), separators=',.')
    r1.plotly_chart(gauge, use_container_width=True)
    with r2:
        st.markdown(f"### Riesgo: <span style='color:{color}'>{nivel}</span>", unsafe_allow_html=True)
        st.write(f'**Acción sugerida:** {accion}')
        st.write(f'La cita quedaría para un **{dia_cita}**.' + (' Ojo: casi no hay citas en fin de semana en los datos.' if dia_cita in ('sabado', 'domingo') else ''))
        st.write(f'Umbral de alerta del modelo: {fmt(UMBRAL * 100)} % (elegido en validación para maximizar el F1).')
        st.write(f'Espera típica estimada para este perfil: **{fmt(espera_est)} días** '
                 f'(error medio del regresor ±{fmt(MET_REG["MAE"])} días). El regresor no usa los días de espera ingresados: '
                 'estima la espera solo con la información del paciente, el barrio y el momento del agendamiento.')
        st.caption('Estimación estadística basada en datos de 2016 de Vitória (Brasil). Es una ayuda para priorizar '
                   'recordatorios, no una decisión sobre la atención del paciente.')

# ------------------------------------------------------------------ 3. segmentación
with tab3:
    st.subheader('Segmentos de pacientes (K-Means, K = 5)')
    st.write('Cada punto es un paciente, proyectado en las dos primeras componentes principales '
             f'({fmt(VAR_PCA * 100, 0)} % de la varianza). Los filtros de edad, sexo y barrio no aplican a esta vista, '
             'que muestra la población completa.')
    muestra = pac.sample(min(8000, len(pac)), random_state=1)
    orden = sorted(pac.segmento.unique())
    fig = px.scatter(muestra, x='pc1', y='pc2', color='segmento', opacity=.55, category_orders={'segmento': orden},
                     color_discrete_map=COLORES_SEG, labels={'pc1': 'Componente 1', 'pc2': 'Componente 2', 'segmento': 'Segmento'},
                     hover_data={'edad': ':.0f', 'n_citas': True, 'espera_media': ':.1f', 'tasa_inasistencia': ':.2f', 'pc1': False, 'pc2': False})
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(height=470, legend=dict(orientation='h', y=-0.15), margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    perfil = pac.groupby('segmento').agg(Pacientes=('edad', 'size'), Edad_media=('edad', 'mean'), Citas_por_paciente=('n_citas', 'mean'),
                                         Tasa_inasistencia=('tasa_inasistencia', 'mean'), Espera_media_dias=('espera_media', 'mean'),
                                         Condiciones_cronicas=('n_condiciones_cronicas', 'mean'), Proporcion_SMS=('prop_sms', 'mean'))
    perfil.insert(1, '% pacientes', perfil.Pacientes / perfil.Pacientes.sum() * 100)
    perfil.columns = [c.replace('_', ' ') for c in perfil.columns]
    st.dataframe(perfil.round(2), use_container_width=True)
    st.info('Los segmentos "Espera larga, no asistieron" y "Espera larga con SMS, asistieron" tienen perfiles parecidos '
            '(una cita, unos 20 días de espera) y se diferencian sobre todo en la cobertura de SMS. Es una asociación '
            'observada: el envío de SMS no fue aleatorio.')

# ------------------------------------------------------------------ 4. desempeño
with tab4:
    st.subheader('Resultados en el conjunto de prueba (16.583 citas no usadas en el entrenamiento)')
    m1, m2 = st.columns(2)
    with m1:
        st.markdown('**Clasificación — XGBoost**')
        st.dataframe(pd.DataFrame(MET_CLF, index=['Prueba']).round(3), use_container_width=True)
        comp = pd.DataFrame({'Modelo': ['XGBoost', 'Random Forest', 'MLP (PyTorch)', 'Logística (baseline)'],
                             'AUC-ROC': [0.740, 0.739, 0.738, 0.729], 'F1': [0.455, 0.455, 0.454, 0.451]})
        st.caption('Comparación de la Fase 3 (prueba):')
        st.dataframe(comp, hide_index=True, use_container_width=True)
    with m2:
        st.markdown('**Regresión de los días de espera — XGBoost Regressor**')
        st.dataframe(pd.DataFrame(MET_REG, index=['Prueba']).round(3), use_container_width=True)
        st.caption('El R² bajo refleja que el dataset no incluye especialidad, profesional ni disponibilidad de agenda, '
                   'que son los determinantes reales de la espera.')
    top = IMP.head(12).iloc[::-1]
    fig = px.bar(x=top.values * 100, y=top.index, orientation='h', color_discrete_sequence=[AZUL],
                 labels={'x': '% de la ganancia total', 'y': ''})
    fig.update_layout(title='Variables más influyentes en el clasificador (importancia por ganancia)', height=430, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)
