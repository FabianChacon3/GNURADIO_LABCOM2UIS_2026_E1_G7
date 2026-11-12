# Proyecto de Multitrayectoria y SDR

**Canal S3 con QPSK y BPSK, prácticas SDR y transmisión de imágenes**
Universidad Industrial de Santander · Grupo Tema 3
Integrantes: Fabián Chacón V., Javier Gómez S. y Juan Santos L.

## Resumen y alcance

El proyecto estudia un canal discreto de dos trayectorias: camino directo y un eco retardado ocho muestras (un símbolo). QPSK es la implementación principal; BPSK ofrece una comparación complementaria bajo el mismo modelo de canal. El análisis Python genera cuatro figuras y sus CSV a partir de un modelo determinista.

Las prácticas TX/RX con SDR e imágenes son actividades complementarias. Los GRC SDR se compilaron, pero no se ejecutó una transmisión por HackRF. Los videos incluidos documentan prácticas suministradas; no validan el caso S3. La captura `images/capturas/Imagenrecibida.jpeg` muestra salida de terminal; no es un archivo reconstruido por el RX.

## Caso S3

| Parámetro | QPSK | BPSK |
|---|---:|---:|
| Símbolos `M` | 4 | 2 |
| Bits por símbolo | 2 | 1 |
| `Rs` | 32 ksym/s | 32 ksym/s |
| `Rb` calculada | 64 kbit/s | 32 kbit/s |
| Muestras por símbolo | 8 | 8 |
| Frecuencia de muestreo | 256 kS/s | 256 kS/s |
| Retardo del eco | 8 muestras = 1 símbolo | 8 muestras = 1 símbolo |
| Amplitud AWGN declarada en el GRC | 0,05 | 0,05 |
| Tap directo | `1+0j` | `1+0j` |

Los dos flujogramas usan las mismas cuatro condiciones del tap retardado: referencia `0+0j`, suave `0,20+0,05j`, media `0,35+0,15j` y fuerte `0,50+0,20j`. En QPSK, la tabla cardinal es `00→1`, `01→j`, `10→−1`, `11→−j`.

Los dos GRC S3 compilaron con GNU Radio 3.10.12 y se iniciaron brevemente en modo sin pantalla para revisar `M`, bits por símbolo, `Rb`, frecuencia de muestreo y las cuatro condiciones. Esto no equivale a una revisión visual manual de los controles y visores. El modelo Python no incorpora AWGN, receptor ni BER.

El [selector de casos S3](docs/selector_casos_s3.html) documenta e interactúa con las cuatro condiciones y los valores de `H(0)` y `H(Rs/2)`.

## Estado de validación

| GRC | Comprobación | Resultado | Evidencia o pendiente |
|---|---|---|---|
| QPSK | Compilación y parámetros | Aprobado | Pruebas reproducibles en `tests/test_grc_validation.py` |
| QPSK | Mapeo bit-símbolo | Aprobado (prueba automática) | Falta captura real de la secuencia conocida en GNU Radio |
| QPSK | Canal, taps y retardo | Aprobado (prueba automática) | Falta captura de la prueba impulsional ejecutada en GNU Radio |
| QPSK | Visores QT | Pendiente por validación manual | Ejecutar el GRC y capturar constelación, tiempo y frecuencia |
| BPSK | Compilación y parámetros | Aprobado | Pruebas reproducibles en `tests/test_grc_validation.py` |
| BPSK | Mapeo bit-símbolo | Aprobado (prueba automática) | Falta captura real de la secuencia conocida en GNU Radio |
| BPSK | Canal, taps y retardo | Aprobado (prueba automática) | Falta captura de la prueba impulsional ejecutada en GNU Radio |
| BPSK | Visores QT | Pendiente por validación manual | Ejecutar el GRC y capturar constelación, tiempo y frecuencia |
| TX imagen | Compilación y protocolo | Aprobado automáticamente | Pruebas de framing, cabecera, CRC y tabla 16-QAM |
| RX imagen | Protocolo, rotaciones y CRC | Aprobado automáticamente | Pruebas unitarias con las cuatro rotaciones |
| TX/RX imagen | Prueba extremo a extremo software | Aprobado automáticamente | Reconstrucción exacta de imagen pequeña en prueba unitaria |
| TX/RX imagen | Transmisión física HackRF | Pendiente por hardware | No se ha ejecutado una transmisión RF |

Las nueve pruebas automáticas se ejecutaron correctamente con el entorno GNU Radio 3.10.12 del proyecto mediante `C:\Users\Fabia\radioconda\python.exe -m unittest discover -s Proyecto_Multitrayectoria\tests -v`. Las capturas QT no se consideran aprobadas hasta guardarse como archivos reales en `images/evidencias_grc/`.

## Procedencia y archivos S3

- GRC QPSK principal: [Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc](src/s3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc)
- Versión QPSK depurada recibida: [prueba.grc](src/s3/QPSK/prueba.grc). Esta es la versión de trabajo con el modelo multitrayectoria, no el GRC original.
- GRC original recibido y conservado: [Modulaciones_basadas_en_constelaciones_AWGN.grc](src/s3/originales/Modulaciones_basadas_en_constelaciones_AWGN.grc). Es la plantilla general de modulaciones y AWGN usada como antecedente.
- GRC BPSK complementario: [Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc](src/s3/BPSK/Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc)
- Script Python recibido junto al flujo original: [Enlace_S3_Multitrayectoria_Grupo3.py](scripts/originales_profesor/Enlace_S3_Multitrayectoria_Grupo3.py)
- Análisis reproducible: [analizar_s3.py](scripts/analisis/analizar_s3.py)
- Datos y figuras numéricas: `data/figuras_s3/`

## Reproducir las figuras

Desde la raíz de `Proyecto_Multitrayectoria/`, ejecute:

```bash
python scripts/analisis/analizar_s3.py
```

Se requieren NumPy y Matplotlib. El script escribe cuatro PNG y cuatro CSV en `data/figuras_s3/`. Usa los taps definidos, una secuencia determinista y prehistoria cero; las salidas son resultados analíticos del modelo, no mediciones de GNU Radio.

Para generar la animación explicativa y la lámina para el informe:

```bash
python scripts/analisis/animar_s3.py
```

El script crea `images/figuras_s3/s3_cambios_parametros_modelo.png`, una copia GIF para el informe y otra en `blog/media/`. La animación recorre referencia, eco suave, medio y fuerte mostrando constelación, secuencia temporal y taps. Es una visualización analítica rotulada; no sustituye capturas reales de GNU Radio.

También genera la variante con ruido `s3_cambios_parametros_modelo_ruido.gif/.png`, usando ruido complejo sintético reproducible con desviación estándar 0,05, y la tabla descargable `data/figuras_s3/s3_tabla_resumen.csv`. La variante con ruido ilustra el efecto esperado de `noise_amp=0.05`, pero tampoco es una medición experimental.

## Prácticas SDR e imágenes

Los flujogramas independientes de TX y RX para imagen son:

- [LAB_TX_16QAM_HackRF_IMAGEN.grc](src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc)
- [LAB_RX_16QAM_HackRF_IMAGEN.grc](src/sdr_imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc)

Ambos compilaron con GNU Radio 3.10.12. El transmisor carga `images/imagenes_sdr/Logouis.png`, la redimensiona a 160×80 RGB y organiza los datos en paquetes. El receptor valida tramas y declara guardar el resultado en `data/resultados/rx_imagen.png` cuando se ejecuta desde `src/sdr_imagen/`. No se hizo una transmisión con hardware ni se dispone de ese PNG de salida.

Los GRC previos se conservan en `src/sdr_imagen/originales/`. Abra los flujogramas SDR desde `src/sdr_imagen/` para que las rutas relativas de la imagen y los resultados correspondan a esa carpeta. Los GRC S3 se pueden abrir desde cualquier carpeta.

## Imágenes, videos y material del curso

El blog carga sus recursos desde `blog/media/`. `images/` mantiene una segunda copia con la misma estructura y contenido: tres videos MP4 H.264/AAC, el logo transmitido, cuatro figuras S3 y la captura de terminal. Los tres videos se comprobaron en la versión publicada de Pages y se reprodujeron en Chrome.

Los materiales de referencia del curso están en `docs/material_curso/`:

- [Guía Estudiante del Proyecto Integrador](docs/material_curso/Guia_Estudiante_Proyecto_Integrador_Comunicaciones_II_2026.pdf)
- [Guía 4: validación final, ajuste y comparación experimental](docs/material_curso/Guia_4_Fase_4_Validacion_final_ajuste_y_comparacion_experimental.pdf)
- [Decisión Técnica Ciega](docs/material_curso/Decision_Tecnica_Ciega_Comunicaciones_II_2026.pdf)

## Blog y GitHub Pages

Abra el blog [localmente](blog/index.html) o en la [versión publicada de GitHub Pages](https://fabianchacon3.github.io/GNURADIO_LABCOM2UIS_2026_E1_G7/). El workflow de publicación está en [deploy-pages.yml](../.github/workflows/deploy-pages.yml), publica únicamente `blog/` y sus recursos, y se ejecuta con los cambios de la rama `integracion-proyecto-comunicaciones-ii`.
