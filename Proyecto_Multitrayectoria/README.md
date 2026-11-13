# Comunicación interior con multitrayectoria: QPSK y BPSK

[Blog público del proyecto](https://fabianchacon3.github.io/GNURADIO_LABCOM2UIS_2026_E1_G7/)

**Integrantes:** Fabián Chacón V., Javier Gómez S. y Juan Santos L.
**Curso:** Comunicaciones II · UIS
**Última actualización:** 12 de noviembre de 2026

## Resumen

Este proyecto estudia un sensor digital que transmite dentro de una bodega o
laboratorio con paredes, estanterías y superficies metálicas. La señal llega
por un camino directo y por una réplica reflejada que se retrasa ocho muestras.
Se implementan QPSK como modulación principal y BPSK como comparación bajo el
mismo canal S3. Se mantienen `Rs=32 ksym/s`, `SPS=8`, `fs=256 kS/s` y cuatro
condiciones controladas del tap complejo. Las pruebas reproducibles generan
constelaciones, respuesta temporal, respuesta impulsional, respuesta
frecuencial y tablas. Las figuras analíticas se distinguen de las capturas
obtenidas desde GNU Radio.

## Decisión técnica y parámetros

QPSK se selecciona como modulación principal porque transmite dos bits por
símbolo manteniendo una constelación compacta y permite observar claramente la
distorsión producida por el eco. BPSK se conserva como comparación de menor
orden y un bit por símbolo.

| Parámetro | QPSK | BPSK |
|---|---:|---:|
| Orden `M` | 4 | 2 |
| Bits por símbolo | 2 | 1 |
| `Rs` | 32 ksym/s | 32 ksym/s |
| `Rb = Rs log2(M)` | 64 kbit/s | 32 kbit/s |
| `SPS` | 8 | 8 |
| `fs = Rs SPS` | 256 kS/s | 256 kS/s |
| Retardo | 8 muestras = 1 símbolo | 8 muestras = 1 símbolo |
| Ruido declarado | 0,05 | 0,05 |

El canal es:

```text
h[n] = delta[n] + c delta[n-8]
y[n] = x[n] + c x[n-8] + w[n]
```

| Prueba | `eco_real` | `eco_imag` | Tap `c` |
|---|---:|---:|---:|
| A · Referencia | 0,00 | 0,00 | `0+0j` |
| B · Suave | 0,20 | 0,05 | `0,20+0,05j` |
| C · Media | 0,35 | 0,15 | `0,35+0,15j` |
| D · Fuerte | 0,50 | 0,20 | `0,50+0,20j` |

En QPSK, el mapeo cardinal es `00 -> 1`, `01 -> j`, `10 -> -1`,
`11 -> -j`. El ancho de banda se interpreta con el pulso rectangular usado
por estos GRC; no se presenta una PSD calibrada cuando la figura es solo la
respuesta del canal.

## GRC funcional

### Archivos modificados

- [QPSK](grc/archivos_modificados/S3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc)
- [BPSK](grc/archivos_modificados/S3/BPSK/Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc)
- [TX 16-QAM de imagen](grc/archivos_modificados/SDR_Imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc)
- [RX 16-QAM de imagen](grc/archivos_modificados/SDR_Imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc)

### Archivos originales o de referencia

Se conservan en [grc/archivos_originales_o_referencia](grc/archivos_originales_o_referencia).
La versión funcional de QPSK es el archivo modificado anterior; no se conserva
`prueba.grc`.

Para ejecutar un GRC, abrirlo con GNU Radio Companion 3.10.12, comprobar las
variables, generar el Python y ejecutar. Los visores QT reciben la salida del
canal; la constelación no es una constelación recuperada por un receptor.

## Tabla de pruebas y evidencias

| Prueba | Objetivo | Evidencia |
|---|---|---|
| A · Referencia | Comportamiento base sin eco | [QPSK](figures/constelacion_o_fsk/QPSK/01_referencia.png), [BPSK](figures/constelacion_o_fsk/BPSK/01_referencia.png) |
| B · Suave | Inicio de la degradación | [QPSK](figures/constelacion_o_fsk/QPSK/02_eco_suave.png), [BPSK](figures/constelacion_o_fsk/BPSK/02_eco_suave.png) |
| C · Media | Condición principal de análisis | [QPSK](figures/constelacion_o_fsk/QPSK/03_eco_medio.png), [BPSK](figures/constelacion_o_fsk/BPSK/03_eco_medio.png) |
| D · Fuerte | Condición de estrés | [QPSK](figures/constelacion_o_fsk/QPSK/04_eco_fuerte.png), [BPSK](figures/constelacion_o_fsk/BPSK/04_eco_fuerte.png) |

Las imágenes con ruido se conservan junto a cada modulación. Las figuras
analíticas y sus tablas están en [data/tablas_de_pruebas](data/tablas_de_pruebas)
y [figures/diagramas_tecnicos](figures/diagramas_tecnicos). No se presentan
como mediciones físicas.

## Estructura del repositorio

```text
Proyecto_Multitrayectoria/
├── README.md
├── grc/
│   ├── archivos_originales_o_referencia/
│   └── archivos_modificados/
├── figures/
│   ├── escenario/
│   ├── psd/
│   ├── constelacion_o_fsk/
│   └── diagramas_tecnicos/
├── multimedia/videos/
├── data/tablas_de_pruebas/
├── docs/
│   ├── Informe_Final_Proyecto.pdf
│   ├── ficha_decision_tecnica.pdf
│   ├── bitacora.md
│   └── material_curso/
├── referencias/fuentes_y_enlaces.md
└── scripts/, tests/
```

La carpeta `blog/` conserva el sitio público y sus recursos locales.

## Reproducibilidad

Desde esta carpeta:

```bash
python scripts/analisis/analizar_s3.py
python scripts/analisis/animar_s3.py
python -m unittest discover -s tests -v
```

Las pruebas automáticas verifican mapeo, tasas, taps, conexiones, framing,
CRC, rotaciones y reconstrucción software de la imagen. Las animaciones son
visualizaciones analíticas; no reemplazan la captura real de una interfaz GRC.

## Documentación y multimedia

- [Informe final IEEE](docs/Informe_Final_Proyecto.pdf)
- [Ficha de decisión técnica](docs/ficha_decision_tecnica.pdf)
- [Bitácora](docs/bitacora.md)
- [Fuentes y enlaces](referencias/fuentes_y_enlaces.md)
- [Selector interactivo S3](docs/selector_casos_s3.html)
- [Blog público](https://fabianchacon3.github.io/GNURADIO_LABCOM2UIS_2026_E1_G7/)

Los videos suministrados están en
[multimedia/videos](multimedia/videos). La socialización de
8–10 minutos y su enlace público deben añadirse cuando estén disponibles.
