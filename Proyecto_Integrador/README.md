# Proyecto integrador de Comunicaciones II

**Canal S3 con QPSK y BPSK, prácticas SDR y transmisión de imágenes**
Universidad Industrial de Santander · Grupo Tema 3
Integrantes: Fabián Chacón V., Javier Gómez S. y Juan Santos L.

## Resumen y alcance

El proyecto estudia un canal discreto de dos trayectorias: camino directo y un eco retardado ocho muestras (un símbolo). QPSK es la implementación principal; BPSK ofrece una comparación complementaria bajo el mismo modelo de canal. El análisis Python genera cuatro figuras y sus CSV a partir de un modelo determinista.

Las prácticas de transmisión y recepción SDR e imágenes son actividades complementarias. Los GRC SDR se compilaron, pero no se ejecutó una transmisión por HackRF. Los videos son material suministrado de prácticas anteriores; no validan el caso S3. Tampoco hay evidencia disponible de un archivo de imagen reconstruido por el receptor.

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

Los dos GRC S3 compilaron con GNU Radio 3.10.12 y se iniciaron brevemente en modo sin pantalla para revisar `M`, bits por símbolo, `Rb`, frecuencia de muestreo y las cuatro condiciones. Esto no equivale a una revisión visual manual de los controles y visores. El modelo de figuras Python no incorpora AWGN, receptor ni BER.

## Archivos principales

- QPSK principal: [Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc](src/s3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc)
- BPSK complementario: [Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc](src/s3/BPSK/Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc)
- GRC fuente preservado: [prueba(1).grc](src/s3/originales/prueba%281%29.grc). El archivo disponible como fuente tenía el nombre `prueba.grc`; la copia incluida conserva su contenido y usa el nombre solicitado.
- Plantilla AWGN de referencia: [Modulaciones_basadas_en_constelaciones_AWGN.grc](src/s3/referencia/Modulaciones_basadas_en_constelaciones_AWGN.grc). Es una referencia general, no sustituye los flujogramas S3.
- Script Python recibido junto al flujo original: [Enlace_S3_Multitrayectoria_Grupo3.py](scripts/originales_profesor/Enlace_S3_Multitrayectoria_Grupo3.py)
- Análisis reproducible: [analizar_s3.py](scripts/analisis/analizar_s3.py)
- Datos y figuras numéricas: `data/figuras_s3/`

## Reproducir las figuras

Desde la raíz de `Proyecto_Integrador/`, ejecute:

```bash
python scripts/analisis/analizar_s3.py
```

Se requieren NumPy y Matplotlib. El script escribe cuatro PNG y cuatro CSV en `data/figuras_s3/`. Usa taps definidos, una secuencia determinista y prehistoria cero; las salidas son resultados analíticos del modelo, no mediciones de GNU Radio.

## Prácticas SDR e imágenes

Los flujogramas independientes de TX y RX para imagen son:

- [LAB_TX_16QAM_HackRF_IMAGEN.grc](src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc)
- [LAB_RX_16QAM_HackRF_IMAGEN.grc](src/sdr_imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc)

Ambos compilaron con GNU Radio 3.10.12. El transmisor carga `images/imagenes_sdr/Logouis.png`, la redimensiona a 160×80 RGB y organiza los datos en paquetes. El receptor valida tramas y declara guardar el resultado en `data/resultados/rx_imagen.png` cuando se ejecuta desde `src/sdr_imagen/`. No se hizo una transmisión con hardware ni se dispone de ese PNG de salida.

Los GRC anteriores se conservan en `src/sdr_imagen/originales/`. Para abrir los flujogramas SDR desde GNU Radio Companion, sitúese primero en `src/sdr_imagen/` para que las rutas relativas de la imagen y los resultados correspondan a esa carpeta. El flujo S3 es de banda base y puede abrirse desde la raíz del proyecto.

## Imágenes, videos y evidencias

El blog carga todos sus recursos desde `blog/media/`. La carpeta `images/` mantiene una segunda copia con la misma estructura y contenido. Se incluyen tres videos (`transmisor.mp4`, `receptoryvalidacionpalabra.mp4`, `Receptorimagen.mp4`), el logo transmitido, cuatro figuras S3 y `capturas/Imagenrecibida.jpeg`. Esta última es una captura de salida de terminal; no es la imagen reconstruida por el RX.

Los materiales de referencia del curso están en `docs/material_curso/`:

- [Guía Estudiante del Proyecto Integrador](docs/material_curso/Guia_Estudiante_Proyecto_Integrador_Comunicaciones_II_2026.pdf)
- [Guía 4: validación final, ajuste y comparación experimental](docs/material_curso/Guia_4_Fase_4_Validacion_final_ajuste_y_comparacion_experimental.pdf)
- [Decisión Técnica Ciega](docs/material_curso/Decision_Tecnica_Ciega_Comunicaciones_II_2026.pdf)

## Blog y publicación

Abra el blog local desde [blog/index.html](blog/index.html). El workflow de Pages está preparado en el repositorio, pero la fuente de GitHub Pages continúa en modo legacy y el workflow aún no se ha publicado. No hay una URL pública verificada para esta versión.