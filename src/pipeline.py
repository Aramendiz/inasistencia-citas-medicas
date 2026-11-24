"""Funciones compartidas del proyecto: limpieza, variables derivadas, partición,
preprocesamiento y entrenamiento de los modelos finales.

Reproduce las decisiones de los Entregables 2 y 3. El tablero (dashboard/app.py)
importa este módulo para entrenar los modelos con los hiperparámetros elegidos
en la Fase 3, de modo que no depende de archivos binarios de una versión concreta
de las librerías.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler, TargetEncoder
from xgboost import XGBClassifier, XGBRegressor

SEMILLA = 42
NOMBRE_CSV = 'KaggleV2-May-2016.csv'

# ---------------------------------------------------------------- variables
NUM = ['edad', 'dias_espera', 'hora_agendamiento', 'citas_previas', 'inasistencias_previas', 'citas_mismo_dia']
TASA = ['tasa_inasistencia_previa']
BIN = ['sexo_f', 'bolsa_familia', 'hipertension', 'diabetes', 'alcoholismo', 'discapacidad',
       'sms_recibido', 'cita_mismo_dia', 'n_condiciones_cronicas']
CAT = ['dia_semana_cita', 'dia_semana_agendamiento', 'grupo_etario']
ALTA = ['barrio']
# Regresión de la espera: sin variables que la revelan (SMS, cita del mismo día, día de la cita)
NUM_R = ['edad', 'hora_agendamiento', 'citas_previas', 'inasistencias_previas', 'citas_mismo_dia']
BIN_R = ['sexo_f', 'bolsa_familia', 'hipertension', 'diabetes', 'alcoholismo', 'discapacidad', 'n_condiciones_cronicas']
CAT_R = ['dia_semana_agendamiento', 'grupo_etario']
VARS_CLUSTER = ['edad', 'log_n_citas', 'tasa_inasistencia', 'log_espera_media', 'n_condiciones_cronicas', 'prop_sms']

DIAS = {0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo'}
GRUPOS_EDAD = ([-1, 12, 18, 35, 60, 200], ['0-12', '13-18', '19-35', '36-60', '60+'])

# Hiperparámetros elegidos en la Fase 3 (RandomizedSearchCV, CV agrupada por paciente)
PARAMS_XGB_CLF = dict(n_estimators=240, max_depth=6, learning_rate=0.03819130560209075, subsample=0.6661067756252009,
                      colsample_bytree=0.6783766633467947, min_child_weight=13, reg_lambda=1.4914817179873872)
PARAMS_XGB_REG = dict(n_estimators=436, max_depth=7, learning_rate=0.022195109122206198, subsample=0.9314950036607718,
                      colsample_bytree=0.5979914312095727, min_child_weight=16, reg_lambda=1.360465183078236)
K_CLUSTERS = 5


def buscar_csv(*carpetas):
    """Devuelve la ruta del CSV buscando en las carpetas habituales del repositorio."""
    raiz = Path(__file__).resolve().parent.parent
    for c in [*carpetas, raiz / 'data', Path('data'), Path('../data'), Path('.')]:
        p = Path(c) / NOMBRE_CSV
        if p.exists():
            return p
    raise FileNotFoundError(f'No se encontró {NOMBRE_CSV}')


class Winsorizador(BaseEstimator, TransformerMixin):
    """Recorta cada columna a los percentiles aprendidos en fit (solo entrenamiento)."""

    def __init__(self, inf=0.0, sup=0.99):
        self.inf, self.sup = inf, sup

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lim_inf_ = np.nanquantile(X, self.inf, axis=0)
        self.lim_sup_ = np.nanquantile(X, self.sup, axis=0)
        return self

    def transform(self, X):
        return np.clip(np.asarray(X, dtype=float), self.lim_inf_, self.lim_sup_)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features)


def cargar_y_preparar(ruta):
    """Limpieza (Fase 2, sección 1) y variables derivadas (Fase 2, sección 2)."""
    mapa = {'PatientId': 'id_paciente', 'AppointmentID': 'id_cita', 'Gender': 'sexo', 'ScheduledDay': 'fecha_agendamiento',
            'AppointmentDay': 'fecha_cita', 'Age': 'edad', 'Neighbourhood': 'barrio', 'Scholarship': 'bolsa_familia',
            'Hipertension': 'hipertension', 'Diabetes': 'diabetes', 'Alcoholism': 'alcoholismo', 'Handcap': 'discapacidad',
            'SMS_received': 'sms_recibido', 'No-show': 'no_asistio'}
    df = pd.read_csv(ruta).rename(columns=mapa)
    df['id_paciente'] = df['id_paciente'].astype('int64').astype(str)
    df['fecha_agendamiento'] = pd.to_datetime(df['fecha_agendamiento'], utc=True)
    df['fecha_cita'] = pd.to_datetime(df['fecha_cita'], utc=True)
    df['inasistencia'] = (df['no_asistio'] == 'Yes').astype(int)
    df['dias_espera'] = (df['fecha_cita'].dt.normalize() - df['fecha_agendamiento'].dt.normalize()).dt.days

    df = df.loc[~((df.edad < 0) | (df.dias_espera < 0))].reset_index(drop=True)
    df['edad'] = df['edad'].astype(float)
    df.loc[df.edad > 110, 'edad'] = np.nan

    df = df.sort_values(['id_paciente', 'fecha_cita', 'fecha_agendamiento']).reset_index(drop=True)
    df['cita_mismo_dia'] = (df.dias_espera == 0).astype(int)
    df['dia_semana_cita'] = df.fecha_cita.dt.dayofweek.map(DIAS)
    df['dia_semana_agendamiento'] = df.fecha_agendamiento.dt.dayofweek.map(DIAS)
    df['hora_agendamiento'] = df.fecha_agendamiento.dt.hour
    df['n_condiciones_cronicas'] = df[['hipertension', 'diabetes', 'alcoholismo']].sum(axis=1)
    df['grupo_etario'] = grupo_etario(df.edad)
    df['citas_mismo_dia'] = df.groupby(['id_paciente', 'fecha_cita']).id_cita.transform('count')
    por_dia = df.groupby(['id_paciente', 'fecha_cita']).agg(n=('id_cita', 'count'), ina=('inasistencia', 'sum')).reset_index()
    g = por_dia.groupby('id_paciente')
    por_dia['citas_previas'] = g.n.cumsum() - por_dia.n
    por_dia['inasistencias_previas'] = g.ina.cumsum() - por_dia.ina
    df = df.merge(por_dia[['id_paciente', 'fecha_cita', 'citas_previas', 'inasistencias_previas']],
                  on=['id_paciente', 'fecha_cita'], how='left')
    df['tasa_inasistencia_previa'] = np.where(df.citas_previas > 0,
                                              df.inasistencias_previas / df.citas_previas.replace(0, 1), np.nan)
    df['sexo_f'] = (df.sexo == 'F').astype(int)
    return df


def grupo_etario(edad):
    g = pd.cut(edad, GRUPOS_EDAD[0], labels=GRUPOS_EDAD[1]).astype(object)
    return g.where(pd.notna(edad), np.nan)


def particionar(df):
    """70/15/15 estratificada por inasistencia y agrupada por paciente (Fase 2, sección 4)."""
    sgkf = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=SEMILLA)
    fold = np.full(len(df), -1)
    for k, (_, idx) in enumerate(sgkf.split(df, df.inasistencia, groups=df.id_paciente)):
        fold[idx] = k
    df = df.copy()
    df['conjunto'] = np.select([fold < 3, fold < 6], ['prueba', 'validacion'], 'entrenamiento')
    return df


def preprocesador(num, tasa, binarias, cat, alta, tipo_objetivo):
    pasos = [('num', Pipeline([('imp', SimpleImputer(strategy='median')), ('win', Winsorizador(0, .99)),
                               ('esc', StandardScaler())]), num),
             ('bin', 'passthrough', binarias),
             ('cat', Pipeline([('imp', SimpleImputer(strategy='most_frequent')),
                               ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat),
             ('alta', TargetEncoder(target_type=tipo_objetivo, random_state=SEMILLA), alta)]
    if tasa:
        pasos.insert(1, ('tasa', Pipeline([('imp', SimpleImputer(strategy='mean', add_indicator=True)),
                                           ('esc', StandardScaler())]), tasa))
    return ColumnTransformer(pasos, verbose_feature_names_out=False)


def entrenar_clasificador(ent):
    ratio = (ent.inasistencia == 0).sum() / (ent.inasistencia == 1).sum()
    modelo = Pipeline([('prep', preprocesador(NUM, TASA, BIN, CAT, ALTA, 'binary')),
                       ('m', XGBClassifier(tree_method='hist', scale_pos_weight=ratio, eval_metric='auc', n_jobs=-1,
                                           random_state=SEMILLA, **PARAMS_XGB_CLF))])
    return modelo.fit(ent, ent.inasistencia)


def entrenar_regresor(ent):
    modelo = Pipeline([('prep', preprocesador(NUM_R, [], BIN_R, CAT_R, ALTA, 'continuous')),
                       ('m', XGBRegressor(tree_method='hist', n_jobs=-1, random_state=SEMILLA, **PARAMS_XGB_REG))])
    return modelo.fit(ent, ent.dias_espera)


def tabla_pacientes(df):
    pac = df.groupby('id_paciente').agg(edad=('edad', 'median'), n_citas=('id_cita', 'count'),
                                        tasa_inasistencia=('inasistencia', 'mean'), espera_media=('dias_espera', 'mean'),
                                        n_condiciones_cronicas=('n_condiciones_cronicas', 'max'),
                                        prop_sms=('sms_recibido', 'mean'), bolsa_familia=('bolsa_familia', 'max'))
    pac['edad'] = pac.edad.fillna(pac.edad.median())
    pac['log_n_citas'] = np.log1p(pac.n_citas)
    pac['log_espera_media'] = np.log1p(pac.espera_media)
    return pac


def entrenar_clustering(pac):
    esc = RobustScaler().fit(pac[VARS_CLUSTER])
    X = esc.transform(pac[VARS_CLUSTER])
    km = KMeans(n_clusters=K_CLUSTERS, n_init=20, random_state=SEMILLA).fit(X)
    pca = PCA(n_components=2, random_state=SEMILLA).fit(X)
    return esc, km, pca, X


def umbral_f1(y, prob):
    from sklearn.metrics import precision_recall_curve
    p, r, u = precision_recall_curve(y, prob)
    f1 = 2 * p * r / np.clip(p + r, 1e-9, None)
    return float(u[np.argmax(f1[:-1])])
