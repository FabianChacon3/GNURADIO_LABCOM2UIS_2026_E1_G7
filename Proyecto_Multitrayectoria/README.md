# Proyecto de Multitrayectoria y SDR

Proyecto final de Comunicaciones II: canal S3 con QPSK/BPSK, validación de
transmisión y recepción 16-QAM con HackRF, e instrumentación BER vs. Eb/N0.

## Alcance y estado

El proyecto conserva el sistema funcional y separa tres tipos de resultado:

- **S3:** modelo de dos trayectorias con camino directo y eco en ocho muestras.
- **TX/RX de imagen:** flujogramas 16-QAM y bloques de framing/deframing.
- **Fase 4 BER:** instrumentación para medir BER vs. Eb/N0 sin reemplazar TX/RX.

La validación previa de TX/RX de imagen se conserva. La instrumentación BER queda
preparada, pero una curva experimental solo es válida cuando `curva_BER.csv`
ha sido generada por el sistema y acompañada por sus parámetros y evidencias.

## Estructura funcional

```text
Proyecto_Multitrayectoria/
├── blog/                         # Sitio local y recursos publicados
├── data/
│   └── figuras_s3/               # CSV y figuras analíticas reproducibles
├── docs/
│   ├── material_curso/           # Guías y documentos de referencia
│   └── selector_casos_s3.html
├── images/
│   ├── evidencias_grc/S3/
│   │   ├── QPSK/                 # Capturas organizadas por condición
│   │   └── BPSK/
│   ├── figuras_s3/               # Figuras analíticas y animaciones
│   ├── imagenes_sdr/             # Imagen transmitida
│   ├── capturas/                 # Capturas de terminal
│   └── videos/                   # Material audiovisual suministrado
├── scripts/analisis/             # Generación de resultados S3
├── src/
│   ├── ber/                      # Instrumentación de la Guía 4
│   ├── s3/                       # GRC QPSK, BPSK y originales
│   └── sdr_imagen/               # GRC TX/RX 16-QAM
└── tests/                        # Pruebas reproducibles
```

No se conserva `QPSK/prueba.grc`: la copia funcional es
`src/s3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc`.

## S3: QPSK y BPSK

| Parámetro | QPSK | BPSK |
|---|---:|---:|
| Orden M | 4 | 2 |
| Bits por símbolo | 2 | 1 |
| Rs | 32 ksym/s | 32 ksym/s |
| Rb | 64 kbit/s | 32 kbit/s |
| SPS | 8 | 8 |
| fs | 256 kS/s | 256 kS/s |
| Retardo | 8 muestras = 1 símbolo | 8 muestras = 1 símbolo |
| Ruido declarado | 0,05 | 0,05 |
| Tap directo | `1+0j` | `1+0j` |

Condiciones del tap retardado:

| Condición | `eco_real` | `eco_imag` | Tap `c` |
|---|---:|---:|---:|
| Referencia | 0,00 | 0,00 | `0+0j` |
| Suave | 0,20 | 0,05 | `0,20+0,05j` |
| Media | 0,35 | 0,15 | `0,35+0,15j` |
| Fuerte | 0,50 | 0,20 | `0,50+0,20j` |

El canal es `h[n]=delta[n]+c delta[n-8]`. En QPSK, el mapeo cardinal es
`00 -> 1`, `01 -> j`, `10 -> -1`, `11 -> -j`. La constelación del GRC se
observa a la salida del canal y no representa símbolos recuperados.

GRC:

- [QPSK](src/s3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc)
- [BPSK](src/s3/BPSK/Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc)

Las capturas disponibles están en
[images/evidencias_grc/S3](images/evidencias_grc/S3). Las figuras analíticas
están en [data/figuras_s3](data/figuras_s3) y
[images/figuras_s3](images/figuras_s3); no deben confundirse con mediciones RF.

## TX/RX 16-QAM de imagen

- [Transmisor](src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc)
- [Receptor](src/sdr_imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc)
- [Originales](src/sdr_imagen/originales)

La validación previa cubre carga de imagen, framing, cabecera, blanqueo, CRC32,
tabla 16-QAM, cuatro rotaciones de fase y reconstrucción de imagen en la prueba
de software. La transmisión física requiere conservar las condiciones de
operación autorizadas, conexión conducida o entorno apantallado y hardware
disponible.

## Fase 4: BER vs. Eb/N0

La guía exige conservar TX/RX y añadir la instrumentación sobre una copia:

```text
SDR Rx -> adaptación radio_rate/bb_rate -> e_EbN0_Sweep -> Rx digital
Bits Tx -> e_BER_Curve <- Bits Rx
                              |
                         QT GUI Vector Sink
```

Instrumentación funcional:

- [Flujograma base BER](src/ber/BER_SDR_INSTRUMENTACION_BASE.grc)
- [e_EbN0_Sweep](src/ber/e_EbN0_Sweep.py)
- [e_BER_Curve](src/ber/e_BER_Curve.py)
- [README de instrumentación](src/ber/README_BER_SDR.txt)

Parámetros iniciales exigidos por la guía:

| Parámetro | Valor |
|---|---:|
| Eb/N0 mínimo | 0 dB |
| Eb/N0 máximo | 14 dB |
| Paso | 1 dB |
| Bits por punto | 100000 |
| Bits de guarda | 1000 |
| Update every | 1000 |
| Rb / bb_rate | Dependen del sistema real |
| delay_bits | Ajustar en condición limpia |

La carpeta todavía no contiene `curva_BER.csv`; por tanto, la medición BER
experimental y su curva deben ejecutarse con el enlace SDR funcional. No se
deben fabricar ni editar manualmente esos datos.

## Reproducibilidad

Desde la raíz de este proyecto:

```bash
python scripts/analisis/analizar_s3.py
python scripts/analisis/animar_s3.py
python -m unittest discover -s tests -v
```

`analizar_s3.py` produce datos y figuras del modelo sin AWGN. `animar_s3.py`
produce las versiones sin ruido y con ruido sintético reproducible, además de
la tabla [s3_tabla_resumen.csv](data/figuras_s3/s3_tabla_resumen.csv).

## Documentación y blog

- [Informe final del proyecto](docs/Informe_Final_Proyecto.pdf)
- [Guía 4 de validación BER](docs/material_curso/Guia_4_Fase_4_Validacion_final_ajuste_y_comparacion_experimental.pdf)
- [Selector interactivo S3](docs/selector_casos_s3.html)
- [Blog local](blog/index.html)
- [README general del repositorio](../README.md)

El blog distingue explícitamente figuras analíticas, capturas GRC, videos
suministrados y mediciones experimentales.
