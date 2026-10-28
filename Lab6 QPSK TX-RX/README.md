# Laboratorio 6: transmisión y recepción de audio QPSK

Este laboratorio estudia la transmisión digital de un audio mediante QPSK en
GNU Radio. El flujo convierte el audio a una representación de 8 bits, lo
modula, añade ruido gaussiano configurable y reconstruye la señal en el
receptor. El propósito es relacionar el nivel relativo de transmisión
(`tx_power_db`), el ruido del canal (`noise_amp`), la constelación recibida y
la fidelidad del audio reconstruido.

El modelo es una simulación educativa de banda base. No implementa una cadena
de radiofrecuencia completa, sincronización de portadora o tiempo, FEC ni una
medida directa de BER. Las métricas del audio permiten evaluar la
reconstrucción, pero no sustituyen la SNR del canal ni la BER.

![Diagrama de comunicación QPSK](docs/diagrama.png)

## Requisitos

- Python 3.x.
- GNU Radio Companion 3.10 o posterior para abrir y ejecutar el flujo.
- Dependencias de análisis: `python -m pip install -r requirements.txt`.

## Uso

Ejecuta los comandos desde la raíz de este laboratorio:

### Flujo automático recomendado

El punto de entrada único detecta la frecuencia de cualquier audio fuente,
lo convierte al formato/tasa que declara el `.grc`, genera caracterizaciones
del original y del audio preparado, y compara la captura RX si ya existe:

```bash
python src/lab6_audio.py
```

También permite indicar la fuente y registrar los parámetros de la captura:

```bash
python src/lab6_audio.py \
    --entrada data/entrada/audio_original.wav \
    --recibido data/resultados/audio_rx_capture.wav \
    --tx-power-db 0 --noise-amp 0 --rx-gain 1 --scale 128 --sps 8
```

La frecuencia de la canción fuente no está fija. El archivo de entrada del
flujo GNU Radio se materializa automáticamente a la frecuencia configurada en
`sample_rate_audio` del `.grc` (actualmente 44.100 Hz), mientras que la
referencia y la captura RX se remuestrean internamente a una tasa común antes
de calcular métricas.
Una captura creada con una configuración anterior puede tener otra frecuencia:
se puede comparar como diagnóstico, pero debe volver a capturarse para
presentarla como resultado del flujo actual.

### Ejecución en GNU Radio

1. La fuente puede tener cualquier frecuencia, cantidad de canales y formato
   compatible con `soundfile`. `lab6_audio.py` crea automáticamente
   `data/entrada/audio_demo.wav`.
2. Abre `src/lab6_tx_rx_audio_qpsk_mejorado.grc` en GNU Radio Companion.
   Como GNU Radio ejecuta el script desde `src/`, el flujo usa rutas
   `../data/entrada/` y `../data/resultados/` internamente.
   Ejecuta primero con `tx_power_db = 0 dB` y `noise_amp = 0`; después cambia
   una variable a la vez. La captura del receptor se escribe en
   `data/resultados/audio_rx_capture.wav`.
   Después de cambiar el `.grc`, usa **Generate flow graph** para regenerar
   `src/QPSK_TX_RX.py`; no ejecutes una versión Python antigua.
3. Detén el flujo antes de iniciar otra prueba para cerrar el WAV. Cambia el
   nombre de cada captura si deseas conservar varias condiciones.
4. Vuelve a ejecutar `python src/lab6_audio.py` para generar las figuras y
   métricas. Los parámetros de la captura se guardan en el JSON.

Consulta [`docs/CONTEXTO_LAB6_AUDIO_QPSK.md`](docs/CONTEXTO_LAB6_AUDIO_QPSK.md)
para la metodología, la interpretación de controles y la matriz experimental.
La plantilla del informe está en
[`docs/plantilla_informe_lab6.md`](docs/plantilla_informe_lab6.md).

## Organización

```text
.
├── 📄README.md
├── 📄requirements.txt
├── 📂src/
│   ├── 📑lab6_tx_rx_audio_qpsk_mejorado.grc
│   ├── 📑QPSK_TX_RX.py
│   ├── 📑lab6_audio.py       # punto de entrada automático
├── 📂data/
│   ├── 📂entrada/       # fuente original y WAV preparado que consume el flujo
│   ├── 📂resultados/    # capturas RX, gráficas y métricas generadas
│   └── 📂evidencia/     # figuras usadas para documentar el laboratorio
└── 📂docs/
    ├── diagrama.png
    └── CONTEXTO_LAB6_AUDIO_QPSK.md
```

`lab6_audio.py` es el único script de Python del flujo y consolida preparación,
caracterización y comparación.

La carpeta `referencia/` se eliminó porque contenía copias obsoletas de
diagramas; el flujo vigente en `src/` es la fuente de verdad. No se generan
archivos de salida en la raíz.

La captura de diagnóstico de 48 kHz estéreo en `data/evidencia/` documenta el
estado inicial y no es un resultado experimental final. Las capturas por
condición deben conservarse con nombres distintos en `data/resultados/`.
El JSON actualmente disponible analiza 20 s y conserva los parámetros
declarados de la captura, pero su correlación es aproximadamente `0.0033` y
su SNR de reconstrucción cruda `-4.57 dB`; por sí solo no demuestra una
recepción fiel. La escucha y la confirmación de GNU Radio siguen pendientes.

## Precauciones

- No subas canciones protegidas por copyright sin autorización; usa audio
  libre o conserva la fuente únicamente de forma local.
