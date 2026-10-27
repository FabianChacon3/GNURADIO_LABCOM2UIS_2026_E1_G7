# Laboratorio 6 — Transmisión y recepción digital de audio QPSK

## 1. Objetivo del paquete

Organizar el flujo de trabajo para estudiar qué ocurre cuando un audio se convierte a símbolos QPSK, atraviesa un canal con ruido aditivo y se reconstruye en el receptor. El laboratorio busca que el estudiante relacione:

- la frecuencia de muestreo y el ancho de banda representable;
- la cuantización del audio antes de la transmisión;
- el nivel relativo de transmisión (`tx_power_db`);
- el ruido añadido al canal (`noise_amp`);
- la constelación recibida y la calidad del audio reconstruido.

El grafo sigue siendo una simulación educativa de banda base. No es una radiofrecuencia física ni una cadena de módem completa: no incorpora sincronización de portadora/tiempo, FEC, tramas, filtrado de coseno alzado, ni medida de BER calibrada.

## 2. Diagnóstico inicial respaldado por el archivo analizado

La captura de análisis del archivo original muestra estos datos:

- Frecuencia de muestreo: **48.000 Hz**.
- Canales: **2 (estéreo)**.
- Duración aproximada: **243,66 s**.
- Frecuencia de Nyquist: **24 kHz**.
- Visualmente, la zona de mayor magnitud está principalmente bajo unos **5 kHz**; hay contenido visible hasta aproximadamente **16–17 kHz**. Estos límites son una lectura de la gráfica, no una estimación exacta de energía acumulada.

El grafo anterior configuraba la salida de audio a **44.100 Hz** y la fuente WAV usaba un único canal. Si se reproduce un archivo de 48 kHz como si sus muestras fueran de 44,1 kHz, sin remuestrear realmente, la velocidad relativa es:

\[
\frac{44.100}{48.000}=0,91875
\]

Por ello el audio puede sonar más lento y grave; la duración teórica cambiaría de 243,66 s a aproximadamente 265,4 s. La corrección adoptada es convertir las muestras a mono y remuestrearlas matemáticamente a 44.100 Hz antes de cargarlas en GNU Radio. No basta con modificar el número de tasa declarado.

### Decisión de entrada

El grafo espera `audio_demo.wav`, **mono, WAV PCM de 16 bits y 44.100 Hz**. El script `preparar_audio.py` crea este archivo desde una fuente compatible con `soundfile`.

Por defecto, el script normaliza el pico a -1 dBFS. Esto cambia el nivel de reproducción, pero mejora el aprovechamiento del cuantizador de 8 bits que existe en el grafo. Para conservar la amplitud relativa original, usar `--sin-normalizar`; si se hace, se debe comprobar que el audio no tenga un pico demasiado bajo para la cuantización actual.

El downmix empleado es el promedio aritmético de L y R. Puede producir cancelación parcial si los canales originales están muy desfasados. Escuchar y analizar el WAV preparado es parte de la validación.

## 3. Arquitectura de la cadena

```text
Archivo original 48 kHz estéreo
        │
        ▼
preparar_audio.py
  downmix + remuestreo real + WAV PCM16 mono, 44.1 kHz
        │
        ▼
Wav File Source (audio_demo.wav)
        │
        ├──► QT GUI Time Sink: forma de onda del audio
        ├──► QT GUI Frequency Sink: espectro del audio de entrada
        │
        ▼
Float to Char (escala 128; cuantización a 8 bits aprox.)
        │
        ▼
Packed to Unpacked (2 bits por símbolo) → QPSK mapper
        │
        ▼
Interpolación ×8 → ganancia TX 10^(tx_power_db/20)
        │
        ▼
Sumador: señal TX + ruido gaussiano complejo
        │
        ├──► Tiempo/espectro del canal
        │
        ▼
Keep 1 in N (N=8) → ganancia RX
        │
        ├──► Constelación de símbolos RX muestreados
        ▼
Decisor QPSK
        │
        ▼
Unpacked to Packed → Char to Float
        │
        ├──► Reproducción en audio_sink
        └──► WAV de captura: audio_rx_capture.wav
```

### Tasa de muestras del flujo

La versión actual representa cada muestra de audio con un byte. Ese byte tiene 8 bits; QPSK transporta 2 bits por símbolo, por lo que se necesitan 4 símbolos QPSK por muestra de audio. Con `Sps=8`:

- tasa de audio: 44.100 muestras/s;
- símbolos QPSK: 44.100 × 4 = **176.400 símbolos/s**;
- tasa compleja después de interpolación: 176.400 × 8 = **1.411.200 muestras complejas/s**.

Este cálculo explica la variable `samp_rate = sample_rate_audio * 4 * Sps`.

## 4. Qué significa cada control

### `tx_power_db`

Es un **nivel/ganancia de transmisión relativo expresado en dB**, no una potencia absoluta en vatios. El bloque usa un multiplicador de amplitud:

\[
A_{TX}=10^{G_{dB}/20}
\]

La potencia relativa resultante cambia como \(10^{G_{dB}/10}\). Por ejemplo, +6 dB multiplica la amplitud por aproximadamente 2 y la potencia por aproximadamente 4; -20 dB multiplica la amplitud por 0,1 y la potencia por 0,01.

Con el ruido fijo, bajar el nivel TX empeora la SNR y debería aumentar los errores de decisión. Con `noise_amp=0`, cambiar `tx_power_db` solo escala los puntos de la constelación; si no hay errores de decisión, el nivel de las muestras de audio reconstruidas no debería variar por esa ganancia.

### `noise_amp`

Controla la amplitud del ruido gaussiano complejo sumado al canal. Es un parámetro lineal de simulación, **no un valor en dB ni una SNR directa**. Para afirmar una SNR del canal hay que medir las potencias de señal y ruido con una definición consistente.

### `rx_gain`

Multiplica la señal recibida después del sumador. En esta estructura también multiplica el ruido junto con la señal; por sí solo no mejora la SNR ideal. No debe confundirse con la ganancia TX.

### `scale`

Controla la escala de cuantización flotante a byte y la operación inversa. El flujo actual transmite una representación de 8 bits por muestra, aunque el archivo de entrada sea PCM16. Esta reducción de resolución es una limitación real del diseño y puede generar distorsión de cuantización.

## 5. Cómo leer las visualizaciones

- **Audio de entrada — forma de onda:** muestra los valores de las muestras en el tiempo. Una ventana de 1.024 muestras a 44,1 kHz abarca aproximadamente 23,2 ms; es más útil para ver oscilaciones que una ventana de varios segundos.
- **Espectro de audio de entrada:** muestra magnitud relativa frente a frecuencia. Con FFT de 4.096 puntos a 44,1 kHz, la separación entre bins es aproximadamente 10,77 Hz. La frecuencia de Nyquist es 22,05 kHz. La gráfica permite ver dónde se concentra el contenido, pero por sí sola no demuestra fidelidad completa.
- **Espectro del canal QPSK:** corresponde a la señal compleja de banda base del canal, muestreada a 1,4112 MHz. No es el espectro del archivo musical.
- **Constelación RX de símbolos muestreados:** muestra los puntos después de la decimación y la ganancia RX, justo antes del decisor. A nivel TX bajo, los puntos se acercan al origen; el ruido relativo se vuelve más importante cuando `noise_amp` permanece fijo.
- **Audio recibido:** muestra muestras reconstruidas después de la decisión QPSK y la conversión de byte a flotante.

El eje vertical de los espectros está normalizado o expresado relativamente, salvo que se calibre explícitamente. No debe interpretarse como potencia acústica o potencia RF absoluta.

## 6. Archivos del paquete

| Archivo | Propósito | Cuándo usarlo |
|---|---|---|
| `src/lab6_tx_rx_audio_qpsk_mejorado.grc` | Grafo maestro de GNU Radio Companion; contiene controles, visualizaciones y captura WAV de RX. | Abrir/editar/ejecutar en GNU Radio Companion. |
| `src/preparar_audio.py` | Convierte la fuente a mono WAV PCM16 y 44,1 kHz; incluye normalización opcional. | Antes de ejecutar el grafo. |
| `src/caracterizar_audio.py` | Caracteriza tasa, canales, duración, pico, RMS y visualiza forma de onda, FFT y espectrograma. | Para documentar el audio original y el WAV preparado. |
| `src/comparar_audio_rx.py` | Compara referencia y captura del receptor; calcula correlación, MSE, SNR de reconstrucción cruda y ajustada a nivel, y ancho de banda acumulado estimado. | Después de capturar `data/resultados/audio_rx_capture.wav`. |
| `requirements.txt` | Dependencias Python de los scripts de análisis/preparación. | Instalar en el entorno Python utilizado. |
| `data/evidencia/analisis_audio_48k_stereo.png` | Captura de las gráficas del archivo inicial. | Evidencia para el informe. |

**Fuente de verdad:** el archivo `.grc` mejorado. Una vez abierto y validado en GNU Radio Companion, generar el Python desde el propio GRC. Los `.py` generados no deben editarse a mano como vía principal, para evitar que diverjan del flujo visual.

## 7. Procedimiento reproducible

### A. Preparar y analizar la referencia

```bash
python -m pip install -r requirements.txt
python src/preparar_audio.py "cancion_original.wav"
python src/caracterizar_audio.py data/entrada/audio_demo.wav --guardar-graficas --max-segundos 0.02
```

Comprueba que el script informa 44.100 Hz, un canal y PCM16. La duración debe ser casi igual a la del original; el remuestreo cambia el número de muestras, no debe cambiar significativamente la duración.

### B. Ejecutar GNU Radio

1. Coloca `audio_demo.wav` en `data/entrada/` o créalo con `src/preparar_audio.py`.
2. Abre `src/lab6_tx_rx_audio_qpsk_mejorado.grc` en GNU Radio Companion y comprueba que no haya bloques desconocidos o errores de validación.
3. Ejecuta primero con `tx_power_db = 0 dB` y `noise_amp = 0` como línea base.
4. Prueba con el ruido fijo y disminuye el nivel TX, por ejemplo 0, -6, -12 y -18 dB.
5. Repite variando `noise_amp`, manteniendo fijo el nivel TX.
6. Cuando termines una captura, detén el flujo para que `Wav File Sink` cierre el encabezado del archivo. Renombra la captura en `data/resultados/` antes de la siguiente prueba, porque `audio_rx_capture.wav` se sobrescribe.

La fuente del grafo repite el audio para permitir mover los controles durante la ejecución. Por eso la captura puede ser más larga que la canción o contener varias vueltas; el comparador utiliza por defecto un tramo máximo de 20 segundos y alinea las señales por correlación.

### C. Comparar calidad

```bash
python src/comparar_audio_rx.py data/entrada/audio_demo.wav data/resultados/audio_rx_capture.wav --max-segundos 20 --guardar
```

El programa muestra y guarda un PNG con forma de onda, espectro relativo y residuo temporal; también genera un JSON de métricas.

### Métricas y límites

- **Correlación temporal:** proximidad de la forma entre referencia y RX; puede ser baja si hay errores o desalineación residual.
- **MSE:** error cuadrático medio de amplitud.
- **SNR de reconstrucción cruda:** penaliza tanto la distorsión como una diferencia de nivel.
- **SNR tras ajuste de nivel:** estima la similitud después de ajustar un único factor de ganancia; no oculta errores no lineales, pero sí elimina parte de la diferencia de volumen.
- **Ancho de banda 95%/99%:** estimación de la frecuencia hasta la que se acumula el 95%/99% de la suma de la densidad espectral discreta estimada por Welch. Es una medida aproximada, no un borde espectral absoluto.

**Estas métricas no son BER del canal.** Para medir BER de forma válida habría que comparar los bits de referencia con los bits recuperados, alineados antes/después del decisor, y contar bits distintos; el análisis WAV aquí implementado mide fidelidad del audio reconstruido.

## 8. Matriz de experimentos sugerida

Mantener `scale=128`, `rx_gain=1` y mismo archivo de referencia para todos los casos. Registrar cada captura con nombre distinto.

| Caso | `tx_power_db` | `noise_amp` | Propósito |
|---|---:|---:|---|
| A — referencia ideal | 0 dB | 0,00 | Confirmar la ruta y la cuantización sin ruido. |
| B — ruido leve | 0 dB | 0,02 | Observar dispersión RX y degradación leve. |
| C — nivel TX menor | -6 dB | 0,02 | Aislar el efecto de reducir TX con ruido fijo. |
| D — nivel TX bajo | -12 dB | 0,02 | Buscar un régimen con más errores. |
| E — ruido mayor | 0 dB | 0,05 | Aislar el efecto de aumentar ruido con TX fijo. |
| F — condición desafiante | -12 dB | 0,05 | Observar interacción de TX bajo y ruido alto. |

Los valores de `noise_amp` son valores iniciales de prueba, no niveles de SNR garantizados. Ajustar si las condiciones no producen diferencias visibles o si el receptor falla desde el primer punto.

Plantilla de resultados:

| Caso | Duración comparada (s) | Correlación | MSE | SNR cruda (dB) | SNR ajustada (dB) | BW 95% RX (Hz) | Observaciones auditivas/constelación |
|---|---:|---:|---:|---:|---:|---:|---|
| A | | | | | | | |
| B | | | | | | | |
| C | | | | | | | |
| D | | | | | | | |
| E | | | | | | | |
| F | | | | | | | |

## 9. Estructura recomendada del repositorio

```text
lab6-tx-rx-audio-qpsk/
├── README.md
├── requirements.txt
├── src/
│   ├── lab6_tx_rx_audio_qpsk_mejorado.grc
│   ├── QPSK_TX_RX.py
│   ├── preparar_audio.py
│   ├── caracterizar_audio.py
│   └── comparar_audio_rx.py
├── data/
│   ├── entrada/                  # fuente original y WAV preparado
│   ├── resultados/               # capturas, figuras y métricas generadas
│   └── evidencia/                # figuras documentales
├── docs/
│   ├── diagrama.png
│   ├── CONTEXTO_LAB6_AUDIO_QPSK.md
│   └── plantilla_informe_lab6.md
```

La carpeta `referencia/` se retiró porque contenía copias obsoletas de
diagramas. El `.grc` en `src/` es la fuente de verdad.

Las salidas generadas deben permanecer en `data/resultados/`; las figuras que
se incorporen al informe deben permanecer en `data/evidencia/`.

Ejemplo de nombres de salidas:

```text
data/
├── entrada/
│   ├── audio_original.wav
│   └── audio_demo.wav
├── resultados/
│   ├── audio_rx_capture.wav
│   ├── *_analisis.png            # figuras generadas
│   ├── *_comparacion.png
│   └── *_metricas.json
└── evidencia/
    └── analisis_audio_48k_stereo.png
```

Recomendaciones:

- Mantener el `.grc` bajo control de versiones como fuente de verdad.
- No versionar archivos temporales/grandes como `data/resultados/audio_rx_capture.wav` si no son evidencia necesaria.
- No incluir canciones protegidas por copyright sin autorización; documentar nombre, licencia y origen, o utilizar un audio libre.
- Versionar los scripts y las instrucciones para que la persona que evalúe pueda recrear los WAV derivados localmente.
- Guardar las salidas de cada experimento junto a un JSON de parámetros (`tx_power_db`, `noise_amp`, `rx_gain`, `scale`, fs, versión de GNU Radio, sistema operativo).
- Mantener originales inmutables; los WAV convertidos son derivados guardados en `data/entrada/`.

## 10. Estructura sugerida del informe

1. **Título y objetivo:** transmisión/recepción digital de audio mediante QPSK y evaluación del efecto del ruido y el nivel TX.
2. **Fundamento teórico:** muestreo y Nyquist, PCM y cuantización, constelación QPSK, relación señal/ruido, error de reconstrucción.
3. **Materiales y herramientas:** versión de GNU Radio, Python y librerías, archivo de entrada y características originales.
4. **Metodología de preparación:** conversión de estéreo a mono, remuestreo 48 kHz → 44,1 kHz, PCM16 y decisión de normalización.
5. **Arquitectura implementada:** diagrama de bloques, tasa de símbolos, `Sps`, cuantización de 8 bits, canal AWGN y receptor.
6. **Experimentos:** condiciones de TX/noise, variables controladas, duración capturada y procedimiento de repetición.
7. **Resultados:** capturas de forma de onda, espectros, constelaciones, tabla de métricas y escucha comparativa.
8. **Discusión:** diferenciar cambios en volumen, cambios de velocidad/tono, errores de cuantización y errores de transmisión.
9. **Limitaciones:** sin BER medida directamente, cuantización de audio a 8 bits, downmix mono, modelo simplificado de canal y falta de sincronización/filtrado de pulso avanzado.
10. **Conclusiones y trabajo futuro:** medición directa de BER, versión de mayor resolución PCM16, estimación de SNR de canal, filtrado de conformación y pruebas con otros archivos.
11. **Reproducibilidad:** comandos usados, versiones, configuración del experimento y ruta al repositorio.

## 11. Estado de validación

Validado en este paquete: sintaxis Python de los scripts, análisis estático de la estructura YAML y referencias entre bloques del `.grc`.

Pendiente en el equipo de laboratorio: abrir el `.grc` en la versión instalada de GNU Radio Companion, generar y ejecutar el flujo, confirmar la ruta de salida de `data/resultados/audio_rx_capture.wav`, escuchar la salida y completar capturas de cada condición experimental. No se afirma que el grafo se haya ejecutado en este entorno, porque GNU Radio Companion no está instalado aquí y no se ha proporcionado el WAV original para una prueba integral.

## Referencias técnicas

- GNU Radio, documentación del QT GUI y controles de variables: https://wiki.gnuradio.org/index.php/Runtime_Updating_Variables
- GNU Radio, bloque Wav File Sink y formato de muestras: https://wiki.gnuradio.org/index.php?title=Wav_File_Sink
- GNU Radio Companion, definición YAML de Wav File Sink: https://github.com/gnuradio/gnuradio/blob/main/gr-blocks/grc/blocks_wavfile_sink.block.yml
