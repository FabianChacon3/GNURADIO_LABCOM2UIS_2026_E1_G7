# Proyecto integrador de Comunicaciones II

**Canal QPSK de dos trayectorias (S3), prácticas SDR y transmisión de imágenes**<br>
Universidad Industrial de Santander · Grupo Tema 3<br>
Integrantes: Fabián Chacón V., Javier Gómez S. y Juan Santos L.

## Resumen

El proyecto organiza y documenta un flujograma GNU Radio de QPSK con un camino directo y un eco retardado un símbolo. También documenta, como actividad complementaria, los flujos SDR de transmisión y recepción de imagen en 16-QAM. Un script Python genera figuras y CSV reproducibles a partir del modelo S3; el [blog](blog/index.html) conserva el diseño didáctico y presenta los materiales con sus límites de evidencia.

## Actividades y alcance

- Se revisó el archivo GRC S3, sus tasas, mapeo, taps, cuatro condiciones de eco y visores. La copia de trabajo está en `src/s3/Enlace_S3_Multitrayectoria_Grupo3.grc`.
- Se añadieron comentarios y documentación a las copias de los flujos TX/RX de imagen HackRF. Los flujos anteriores de trama de texto se guardan en `src/sdr_imagen/originales/`.
- Se preparó `src/s3/analizar_s3.py` para generar la respuesta impulsional, la respuesta frecuencial, constelaciones y secuencias temporales del modelo.
- Se inspeccionaron videos de clase de TX y RX. Los archivos se enlazan desde `organizar/` y no se duplican.

La revisión GRC fue estática: en este entorno no están disponibles GNU Radio Companion, GNU Radio, PyQt5 ni HackRF. No se afirma una ejecución del GRC S3 ni una transmisión de imagen verificada. No se encontró el PNG reconstruido `rx_imagen.png` entre los materiales recibidos. El modelo de análisis no incluye AWGN, receptor ni BER; la propuesta de la Guía 4 se conserva sin implementar.

## Caso S3

El mapeo QPSK del GRC, con los dos bits en orden MSB primero, es `00→1`, `01→j`, `10→−1` y `11→−j`. Los parámetros principales son:

| Parámetro | Valor |
|---|---:|
| `Rs` / `Rb` | 32 ksym/s / 64 kbit/s |
| `SPS` / `fs` | 8 / 256 kS/s |
| Retardo | 8 muestras = 1 símbolo = 31,25 µs |
| Camino directo | 1 en el tap de índice 0 |
| Ruido declarado en el GRC | 0,05 |
| Interpolación | Pulso rectangular, `h=[1]*SPS` |

Los taps de eco son `0`, `0,20+0,05j`, `0,35+0,15j` y `0,50+0,20j` para referencia, suave, media y fuerte. En el GRC, la salida del canal alimenta los visores de constelación, tiempo y frecuencia. El visor de frecuencia muestra ganancia relativa; no es una PSD calibrada. El flujo no tiene receptor digital ni medidor BER.

## Prácticas SDR e imagen

Los flujos `src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc` y `LAB_RX_16QAM_HackRF_IMAGEN.grc` describen una cadena distinta del caso S3. El TX lee `assets/Logouis.png`, la convierte a 160×80 RGB y la divide en paquetes con cabecera, preámbulo, blanqueo y CRC32. El RX sincroniza, prueba rotaciones de fase, valida CRC y declara reensamblar la imagen en `data/resultados/rx_imagen.png`.

Los valores guardados en estos archivos incluyen 16-QAM, `Rs=8 ksym/s`, `Rb=32 kbit/s`, `SPS=8`, tasa base 64 kS/s, tasa de radio 2 MS/s y filtro RRC con β=0,5 y span 11. Son parámetros declarados por los GRC; no se infieren como valores de una sesión de video. Consulte [Prácticas SDR](docs/PRACTICAS_SDR.md) y [Parámetros](docs/PARAMETROS.md) para el detalle y alcance.

## Organización

```text
Proyecto_Integrador/
├── blog/index.html
├── data/figuras/s3/             # PNG y CSV del modelo analítico
├── docs/                        # Guías, parámetros, referencias y bitácora
└── src/
    ├── s3/                      # GRC S3, referencias y script Python
    └── sdr_imagen/              # GRC TX/RX, logo, resultados y originales
```

Los archivos de origen recibidos permanecen en `../organizar/`. El inventario está en [`../INVENTARIO_MATERIALES.md`](../INVENTARIO_MATERIALES.md), y la correspondencia y diagnóstico iniciales en [`../INFORME_AUDITORIA_INICIAL.md`](../INFORME_AUDITORIA_INICIAL.md).

## Ejecución

Desde la carpeta `Proyecto_Integrador/`, genere las figuras analíticas con:

```bash
python src/s3/analizar_s3.py
```

El script requiere NumPy y Matplotlib y escribe cuatro archivos PNG y cuatro CSV en `data/figuras/s3/`. Cada salida describe el modelo determinista sin AWGN; no contiene mediciones de GNU Radio, PSD ni BER. Consulte [Documentación del script y las figuras](docs/FIGURAS_S3.md).

Para inspeccionar los flujos, abra los archivos `.grc` desde GNU Radio Companion. El caso S3 es una simulación de banda base. Los flujos SDR TX y RX se abren por separado y requieren los bloques y el hardware disponibles en el laboratorio. Las rutas y pasos están en la [Guía de GNU Radio](docs/GUIA_GNU_RADIO.md).

## Documentación

- [Guía de GNU Radio Companion](docs/GUIA_GNU_RADIO.md)
- [Parámetros documentados](docs/PARAMETROS.md)
- [Prácticas SDR e imagen](docs/PRACTICAS_SDR.md)
- [Script y figuras S3](docs/FIGURAS_S3.md)
- [Alcance de Guía 4 y BER](docs/VALIDACION_GUIA4.md)
- [Referencias y trazabilidad](docs/REFERENCIAS.md)
- [Bitácora de modificaciones](docs/BITACORA.md)
- [Blog de divulgación](blog/index.html)

La inspección estática de YAML y la ejecución del script analítico se realizaron en este entorno. La generación y ejecución de flujogramas GNU Radio, la prueba TX/RX con HackRF y la reconstrucción de una imagen requieren validación manual con el entorno de laboratorio. No se implementó la instrumentación BER de la Guía 4 ni se publicó el sitio.
