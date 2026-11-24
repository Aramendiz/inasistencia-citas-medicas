const pptxgen = require('pptxgenjs');
const path = require('path');
const { applyTheme } = require('/root/.claude/skills/synced/6c1e15ac-fefc-4131-b416-b79ab45f8b14_6b269754-241d-49ac-9eb9-8beff41efb21/pptx/scripts/apply_theme.js');

const FIG = path.join(__dirname, '..', 'figs');
const OUT = path.join(__dirname, 'Sustentacion_Inasistencia.pptx');

const THEME = {
  name: 'Inasistencia', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1B2A33', lt1: 'FFFFFF', dk2: '0B4F6C', lt2: 'EEF4F7', accent1: '0B4F6C', accent2: 'D1495B',
            accent3: '2E8B83', accent4: 'E39B2D', accent5: '7B5EA7', accent6: '8A99A6', hlink: '0B4F6C', folHlink: '7B5EA7' },
};
const HEX = { teal: '0B4F6C', coral: 'D1495B', green: '2E8B83', gold: 'E39B2D', grey: '8A99A6', grid: 'DCE5EA', text: '1B2A33' };

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = 'Jairo Teófilo Araméndiz Pinzón';
pres.title = 'Predicción y caracterización de la inasistencia a citas médicas';
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: 'PORTADA', background: { color: THEME.colors.dk2 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.8, y: 2.0, w: 11.5, h: 1.9, fontSize: 40, bold: true, color: C.background1, valign: 'bottom' }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.8, y: 4.15, w: 11.5, h: 1.8, fontSize: 18, color: C.background2, valign: 'top' }, text: '' } },
  ],
});
pres.defineSlideMaster({
  title: 'CONTENIDO', background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontSize: 32, bold: true, color: C.text2, valign: 'middle' }, text: '' } },
    { text: { text: 'Proyecto Integrador · Ciencia de Datos · Universidad de La Salle', options: { x: 0.6, y: 7.05, w: 8, h: 0.3, fontSize: 10, color: '8A99A6' } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.6, h: 0.3, fontSize: 10, color: '8A99A6' },
});

let n = 0;
const card = (s, x, y, w, h, fill) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: `tarjeta_${++n}` });
const txt = (s, t, o) => s.addText(t, { isTextBox: true, margin: 0, fontSize: 16, color: C.text1, valign: 'top', ...o });
const stat = (s, x, y, w, num, label, col) => {
  txt(s, num, { x, y, w, h: 0.9, fontSize: 48, bold: true, color: col, fontFace: 'Cambria' });
  txt(s, label, { x, y: y + 0.95, w, h: 0.7, fontSize: 14, color: C.text1 });
};
const chartBase = (title) => ({
  showTitle: true, title, titleFontSize: 14, titleColor: HEX.text, titleFontFace: '+mn-lt',
  catAxisLabelColor: '4A5A66', valAxisLabelColor: '4A5A66', catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt',
  catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, valGridLine: { color: HEX.grid, size: 0.5 }, catGridLine: { style: 'none' },
  showValue: true, dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', dataLabelColor: HEX.text,
});

// 1. Portada ------------------------------------------------------------------
pres.addSection({ title: 'Introducción' });
let s = pres.addSlide({ masterName: 'PORTADA', sectionTitle: 'Introducción' });
s.addText('Predicción y caracterización de la inasistencia a citas médicas de consulta externa', { placeholder: 'title' });
s.addText([{ text: 'Jairo Teófilo Araméndiz Pinzón', options: { bold: true, breakLine: true } },
           { text: 'Maestría en Inteligencia Artificial · Universidad de La Salle', options: { breakLine: true } },
           { text: 'Ciencia de Datos · Docente: Fabián Camilo Castro Riveros · Noviembre de 2026' }], { placeholder: 'body' });
s.addNotes('Buenos días. Presento el proyecto integrador: un modelo para anticipar qué pacientes no asistirán a su cita de consulta externa, estimar su tiempo de espera y segmentarlos, con un tablero desplegado en vivo. Este trabajo se conecta con mi proyecto de grado, AgendamientoIA. (30 segundos)');

// 2. Problema ------------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Introducción' });
s.addText('Una de cada cinco citas se pierde', { placeholder: 'title' });
card(s, 0.6, 1.6, 3.8, 2.4, THEME.colors.lt2); stat(s, 0.9, 1.85, 3.3, '20,2 %', 'de las 110.527 citas terminó en inasistencia', HEX.coral);
card(s, 4.75, 1.6, 3.8, 2.4, THEME.colors.lt2); stat(s, 5.05, 1.85, 3.3, '62.299', 'pacientes de la red pública de Vitória (Brasil), 2016', HEX.teal);
card(s, 8.9, 1.6, 3.8, 2.4, THEME.colors.lt2); stat(s, 9.2, 1.85, 3.3, '24 h', 'antes de la cita, AgendamientoIA ya envía el recordatorio por WhatsApp', HEX.green);
txt(s, 'Pregunta principal', { x: 0.6, y: 4.45, w: 12, h: 0.4, fontSize: 20, bold: true, color: C.text2, fontFace: 'Cambria' });
txt(s, '¿Qué características del paciente y del agendamiento permiten anticipar la inasistencia, y cómo usar esos patrones para priorizar recordatorios automáticos?',
    { x: 0.6, y: 4.95, w: 12, h: 0.8, fontSize: 18, italic: true });
txt(s, 'Dataset: Medical Appointment No Shows (Kaggle, CC BY-NC-SA 4.0). Sirve como proxy mientras el piloto de AgendamientoIA genera datos propios.',
    { x: 0.6, y: 6.0, w: 12, h: 0.5, fontSize: 13, color: '5A6A76' });
s.addNotes('Cuando un paciente no asiste ni cancela, el cupo se pierde. En este dataset falta el 20 % de las citas. Mi tesis, AgendamientoIA, ya envía recordatorios por WhatsApp; la pregunta es a quién priorizar. Como el piloto aún no tiene datos públicos suficientes, uso este dataset abierto de Brasil como referencia. (1 minuto)');

// 3. Metodología --------------------------------------------------------------
pres.addSection({ title: 'Metodología' });
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Metodología' });
s.addText('Cuatro fases sobre el mismo dataset', { placeholder: 'title' });
const fases = [
  ['1', 'EDA', 'Calidad de datos, χ², correlaciones. Hallazgo: la espera manda.'],
  ['2', 'Preparación', '11 variables derivadas, partición 70/15/15 agrupada por paciente, pipelines sin fuga.'],
  ['3', 'Modelado', 'Random Forest, XGBoost, MLP en PyTorch, ElasticNet, K-Means y Ward. CV + SHAP.'],
  ['4', 'Despliegue', 'Tablero Streamlit con predicción en vivo y mapa de segmentos.'],
];
fases.forEach(([num, t, d], i) => {
  const x = 0.6 + i * 3.1;
  s.addShape(pres.shapes.OVAL, { x: x + 1.05, y: 1.75, w: 0.8, h: 0.8, fill: { color: HEX.teal }, line: { color: HEX.teal }, objectName: `fase_${num}` });
  txt(s, num, { x: x + 1.05, y: 1.75, w: 0.8, h: 0.8, fontSize: 24, bold: true, color: C.background1, align: 'center', valign: 'middle' });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 2.0, y: 2.15, w: 2.05, h: 0, line: { color: HEX.grey, width: 1.5, endArrowType: 'triangle' }, objectName: `flecha_${num}` });
  card(s, x, 2.9, 2.9, 2.3, THEME.colors.lt2);
  txt(s, t, { x: x + 0.25, y: 3.1, w: 2.4, h: 0.5, fontSize: 20, bold: true, color: C.text2, fontFace: 'Cambria' });
  txt(s, d, { x: x + 0.25, y: 3.7, w: 2.4, h: 1.4, fontSize: 15 });
});
txt(s, 'El conjunto de prueba (16.583 citas) se usó una sola vez, al final, con los modelos ya elegidos.', { x: 0.6, y: 5.6, w: 12, h: 0.4, fontSize: 15, color: '5A6A76' });
s.addNotes('El proyecto es uno solo construido por capas. Fase 1: exploración. Fase 2: limpieza y variables, con una partición agrupada por paciente para que ninguna persona quede en entrenamiento y prueba a la vez. Fase 3: modelos con búsqueda de hiperparámetros por validación cruzada. Fase 4: el tablero. La prueba se usó una sola vez. (1 minuto 15 segundos)');

// 4. EDA ----------------------------------------------------------------------
pres.addSection({ title: 'Resultados' });
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Resultados' });
s.addText('A mayor espera, mayor inasistencia', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: '% inasistencia', labels: ['Mismo día', '1-7 días', '8-30 días', '>30 días'], values: [4.7, 24.2, 31.7, 33.0] }],
  { ...chartBase('% de inasistencia según días de espera'), x: 0.6, y: 1.5, w: 6.0, h: 4.6, barDir: 'col', chartColors: [HEX.teal], showLegend: false,
    dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisMaxVal: 40, valAxisLabelFormatCode: '0' });
s.addChart(pres.charts.BAR, [
  { name: 'Sin SMS', labels: ['1-7 días', '8-30 días', '>30 días'], values: [24.4, 35.6, 37.5] },
  { name: 'Con SMS', labels: ['1-7 días', '8-30 días', '>30 días'], values: [23.8, 29.1, 30.2] }],
  { ...chartBase('Mismo tramo de espera: con SMS se falta menos'), x: 6.9, y: 1.5, w: 5.8, h: 4.6, barDir: 'col', barGrouping: 'clustered',
    chartColors: [HEX.grey, HEX.coral], showLegend: true, legendPos: 'b', legendFontSize: 12, legendFontFace: '+mn-lt',
    dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisMaxVal: 40, valAxisLabelFormatCode: '0' });
txt(s, 'Sin estratificar, el SMS parece aumentar la inasistencia (27,6 % frente a 16,7 %): solo se envió a citas con 3 o más días de espera.',
    { x: 0.6, y: 6.25, w: 12.1, h: 0.6, fontSize: 14, color: '5A6A76' });
s.addNotes('El hallazgo central del EDA: la inasistencia pasa de 5 % en citas del mismo día a 33 % con más de un mes. Y una trampa: comparado directamente, el SMS parece empeorar la asistencia, pero es porque solo se envía a citas lejanas. Comparando dentro del mismo tramo de espera, con SMS se falta entre 6 y 7 puntos menos. Es una asociación, no prueba causal. (1 minuto 30 segundos)');

// 5. Clasificación ------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Resultados' });
s.addText('XGBoost detecta 3 de cada 4 inasistencias', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'AUC-ROC (prueba)', labels: ['Logística (base)', 'MLP (PyTorch)', 'Random Forest', 'XGBoost'], values: [0.729, 0.738, 0.739, 0.740] }],
  { ...chartBase('AUC-ROC en el conjunto de prueba'), x: 0.6, y: 1.5, w: 7.2, h: 4.8, barDir: 'bar', chartColors: [HEX.teal], showLegend: false,
    dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.000', valAxisMinVal: 0.70, valAxisMaxVal: 0.75, valAxisLabelFormatCode: '0.00' });
card(s, 8.2, 1.5, 4.5, 4.8, THEME.colors.lt2);
stat(s, 8.5, 1.75, 4.0, '77 %', 'de las inasistencias detectadas (2.578 de 3.349)', HEX.coral);
txt(s, [{ text: 'F1 = 0,455 · umbral 0,52 elegido en validación', options: { bullet: true, breakLine: true } },
        { text: 'Los cuatro modelos quedan a 0,01 de AUC: el límite está en la información del dataset', options: { bullet: true, breakLine: true } },
        { text: 'Un falso positivo cuesta solo un mensaje extra', options: { bullet: true } }],
    { x: 8.5, y: 3.6, w: 4.0, h: 2.6, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes('Comparé Random Forest, XGBoost y un perceptrón multicapa en PyTorch contra la regresión logística. Los tres superan la base, y XGBoost queda primero con AUC de 0,74; detecta el 77 % de las inasistencias. La mejora es pequeña: tres algoritmos muy distintos llegan al mismo techo, lo que indica que falta información en los datos, no capacidad del modelo. Para recordatorios basta, porque una falsa alarma es solo un mensaje más. (1 minuto 30 segundos)');

// 6. SHAP ---------------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Resultados' });
s.addText('Qué mira el modelo: espera, edad e historial', { placeholder: 'title' });
s.addImage({ path: path.join(FIG, 'shap.png'), x: 0.6, y: 1.4, w: 5.3, h: 5.45, altText: 'Gráfico SHAP del clasificador XGBoost' });
const shapPts = [
  ['Espera larga', 'Es la variable de mayor peso; las citas del mismo día bajan el riesgo.', HEX.teal],
  ['Edad', 'Los jóvenes faltan más; los mayores de 60, menos.', HEX.teal],
  ['Historial', 'Cada inasistencia previa sube el riesgo de la siguiente.', HEX.teal],
  ['SMS', 'Con la espera controlada, recibir SMS reduce el riesgo estimado.', HEX.coral],
];
shapPts.forEach(([t, d, col], i) => {
  const y = 1.6 + i * 1.3;
  s.addShape(pres.shapes.OVAL, { x: 6.5, y: y + 0.05, w: 0.45, h: 0.45, fill: { color: col }, line: { color: col }, objectName: `punto_shap_${i}` });
  txt(s, t, { x: 7.2, y, w: 5.5, h: 0.45, fontSize: 20, bold: true, color: C.text2, fontFace: 'Cambria' });
  txt(s, d, { x: 7.2, y: y + 0.5, w: 5.5, h: 0.7, fontSize: 15 });
});
s.addNotes('Con SHAP vemos por qué el modelo decide. La espera domina. Los jóvenes faltan más. El historial de inasistencias suma riesgo. Y el SMS, una vez el modelo controla la espera, reduce el riesgo: el mismo resultado del análisis estratificado, por un camino distinto. (1 minuto)');

// 7. Regresión ----------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Resultados' });
s.addText('La espera depende de la agenda, no del paciente', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'R² (prueba)', labels: ['Lineal (base)', 'ElasticNet', 'XGBoost'], values: [0.077, 0.077, 0.138] }],
  { ...chartBase('R² de la regresión de días de espera (prueba)'), x: 0.6, y: 1.5, w: 6.4, h: 4.8, barDir: 'col', chartColors: [HEX.gold], showLegend: false,
    dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.000', valAxisMaxVal: 0.2, valAxisLabelFormatCode: '0.00' });
card(s, 7.4, 1.5, 5.3, 4.8, THEME.colors.lt2);
stat(s, 7.7, 1.75, 4.8, '±10 días', 'error absoluto medio de XGBoost (RMSE 14,1)', HEX.gold);
txt(s, [{ text: 'XGBoost casi duplica el R² lineal, pero sigue siendo bajo', options: { bullet: true, breakLine: true } },
        { text: 'ElasticNet no mejora: no hay sobreajuste, falta información', options: { bullet: true, breakLine: true } },
        { text: 'El dataset no trae especialidad, profesional ni cupos disponibles', options: { bullet: true } }],
    { x: 7.7, y: 3.6, w: 4.8, h: 2.6, fontSize: 15, paraSpaceAfter: 8 });
s.addNotes('La regresión es el resultado más débil y lo reporto así. XGBoost llega a R² de 0,14 y se equivoca en unos 10 días. ElasticNet no ayuda porque no hay sobreajuste que corregir: lo que falta son variables de oferta, como especialidad o cupos disponibles. Excluí el SMS y el día de la cita porque revelan la espera. (1 minuto)');

// 8. Segmentación -------------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Resultados' });
s.addText('Cinco perfiles de pacientes', { placeholder: 'title' });
const hdr = (t) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: HEX.teal }, fontSize: 14 } });
const filas = [
  ['Citas cercanas, asistieron', '33 %', '29', '5', '1 %', '0 %'],
  ['Usuarios frecuentes (3,7 citas)', '21 %', '34', '10', '35 %', '25 %'],
  ['Espera larga con SMS', '19 %', '38', '20', '91 %', '0 %'],
  ['Adultos mayores crónicos', '14 %', '62', '7', '16 %', '5 %'],
  ['Espera larga, no asistieron', '13 %', '33', '19', '46 %', '100 %'],
];
s.addTable([[hdr('Segmento'), hdr('% pacientes'), hdr('Edad'), hdr('Espera (días)'), hdr('% SMS'), hdr('Inasistencia')],
  ...filas.map((f, i) => f.map((c, j) => ({ text: c, options: { fontSize: 14, color: HEX.text, bold: j === 0,
    fill: { color: (i === 2 || i === 4) ? 'FBE9EC' : (i % 2 ? 'F4F8FA' : 'FFFFFF') }, align: j ? 'center' : 'left' } })))],
  { x: 0.6, y: 1.5, w: 12.1, colW: [4.1, 1.6, 1.2, 1.8, 1.5, 1.9], rowH: 0.55, border: { type: 'solid', color: HEX.grid, pt: 0.5 }, valign: 'middle', objectName: 'tabla_segmentos' });
txt(s, 'K-Means con K = 5 (silueta 0,349). K = 2 se descartó porque solo separa a quien faltó de quien asistió. Ward coincide en un 65 % (ARI = 0,65).',
    { x: 0.6, y: 5.1, w: 12.1, h: 0.6, fontSize: 14, color: '5A6A76' });
txt(s, 'Las filas resaltadas tienen el mismo perfil (una cita, ~20 días de espera) y se diferencian sobre todo en la cobertura de SMS.',
    { x: 0.6, y: 5.8, w: 12.1, h: 0.6, fontSize: 16, bold: true, color: HEX.coral });
s.addNotes('El clustering encontró cinco perfiles. Descarté K igual a 2 aunque tenía la mejor silueta, porque solo separaba a quien faltó de quien asistió. Las dos filas resaltadas son lo más interesante: pacientes con una cita y unos 20 días de espera; los que recibieron SMS en un 91 % asistieron todos, y los que no, faltaron. Es retrospectivo y observacional, pero refuerza la hipótesis del recordatorio. (1 minuto 30 segundos)');

// 9. Tablero ------------------------------------------------------------------
pres.addSection({ title: 'Tablero y cierre' });
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Tablero y cierre' });
s.addText('Tablero en vivo: demostración', { placeholder: 'title' });
s.addImage({ path: path.join(FIG, 'tablero_prediccion.png'), x: 0.6, y: 1.45, w: 5.94, h: 5.4, altText: 'Módulo de predicción en vivo del tablero' });
const mods = [['Filtros', 'Fecha, sexo, edad, espera, SMS, barrio y segmento'], ['Tarjetas KPI', 'Citas, inasistencia, espera, cobertura SMS, AUC'],
              ['Predicción en vivo', 'Probabilidad, nivel de riesgo y acción de recordatorio sugerida'], ['Segmentación', 'Mapa PCA interactivo y perfiles']];
mods.forEach(([t, d], i) => {
  const y = 1.5 + i * 1.25;
  card(s, 7.3, y, 5.4, 1.05, THEME.colors.lt2);
  txt(s, t, { x: 7.55, y: y + 0.12, w: 5.0, h: 0.4, fontSize: 18, bold: true, color: C.text2, fontFace: 'Cambria' });
  txt(s, d, { x: 7.55, y: y + 0.55, w: 5.0, h: 0.4, fontSize: 14 });
});
txt(s, 'Streamlit Community Cloud · URL: [pegar enlace]', { x: 7.3, y: 6.55, w: 5.4, h: 0.35, fontSize: 13, color: '5A6A76' });
s.addNotes('Ahora la demostración (2 minutos). Paso 1: mostrar las tarjetas y aplicar un filtro, por ejemplo solo citas con más de 30 días de espera: la inasistencia sube. Paso 2: pestaña de predicción, ingresar un paciente joven con 30 días de espera y sin SMS; ver riesgo alto y la acción sugerida. Activar el SMS y comparar. Paso 3: pestaña de segmentación, pasar el cursor por el mapa. El tablero reentrena los modelos al iniciar con los hiperparámetros de la Fase 3, así que no depende de archivos binarios.');

// 10. Implicaciones -----------------------------------------------------------
s = pres.addSlide({ masterName: 'CONTENIDO', sectionTitle: 'Tablero y cierre' });
s.addText('De los datos a la política de recordatorios', { placeholder: 'title' });
const recs = [['Priorizar', 'Citas con más de una semana de espera reciben recordatorio con confirmación.', HEX.teal],
              ['Intensificar', 'Pacientes con inasistencias previas: CONFIRMAR / CANCELAR por WhatsApp.', HEX.gold],
              ['Reasignar', 'Riesgo alto: ofrecer fecha más cercana o liberar el cupo a lista de espera.', HEX.coral]];
recs.forEach(([t, d, col], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 1.5, 3.85, 2.6, THEME.colors.lt2);
  s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 1.75, w: 0.55, h: 0.55, fill: { color: col }, line: { color: col }, objectName: `rec_${i}` });
  txt(s, t, { x: x + 1.0, y: 1.78, w: 2.7, h: 0.5, fontSize: 20, bold: true, color: C.text2, fontFace: 'Cambria' });
  txt(s, d, { x: x + 0.3, y: 2.55, w: 3.3, h: 1.4, fontSize: 15 });
});
txt(s, 'Limitaciones', { x: 0.6, y: 4.45, w: 12, h: 0.4, fontSize: 20, bold: true, color: C.text2, fontFace: 'Cambria' });
txt(s, [{ text: 'Seis semanas de 2016 en una ciudad brasileña: la transferencia a Colombia debe validarse con el piloto', options: { bullet: true, breakLine: true } },
        { text: 'El SMS no se envió al azar: su efecto es una asociación, no causalidad', options: { bullet: true, breakLine: true } },
        { text: 'Variables como barrio y Bolsa Família exigen revisar equidad: riesgo alto debe significar más apoyo, no menos citas', options: { bullet: true } }],
    { x: 0.6, y: 4.95, w: 12.1, h: 1.8, fontSize: 15, paraSpaceAfter: 6 });
s.addNotes('Qué hago con esto en AgendamientoIA: priorizar los recordatorios en citas lejanas, pedir confirmación explícita a quienes ya han faltado y, en riesgo alto, ofrecer una fecha más cercana o liberar el cupo. Las limitaciones: datos de Brasil de 2016, efecto del SMS observacional y un tema de equidad: el modelo debe usarse para apoyar más, nunca para negar citas. (1 minuto 15 segundos)');

// 11. Cierre ------------------------------------------------------------------
s = pres.addSlide({ masterName: 'PORTADA', sectionTitle: 'Tablero y cierre' });
s.addText('Conclusiones y trabajo futuro', { placeholder: 'title' });
s.addText([{ text: 'Clasificación: AUC 0,740 y 77 % de inasistencias detectadas; objetivo cumplido', options: { bullet: true, breakLine: true } },
           { text: 'La espera no se predice con datos del paciente: depende de la oferta de agenda', options: { bullet: true, breakLine: true } },
           { text: 'Siguiente paso: reentrenar con datos del piloto (especialidad, EPS, respuesta en WhatsApp) y medir el efecto del recordatorio con un experimento', options: { bullet: true, breakLine: true } },
           { text: 'Gracias · Preguntas', options: { bold: true } }], { placeholder: 'body', fontSize: 18, paraSpaceAfter: 8 });
s.addNotes('Cierro: el modelo de clasificación cumple el objetivo; la regresión mostró que la espera depende de la agenda; y el siguiente paso es llevar el modelo al piloto de AgendamientoIA y medir con un experimento el efecto real del recordatorio. Gracias, quedo atento a sus preguntas. (45 segundos)');

pres.writeFile({ fileName: OUT }).then(async () => { await applyTheme(OUT, THEME); console.log('ok', OUT); });
