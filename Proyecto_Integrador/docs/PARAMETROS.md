# Parámetros documentados

Los valores se transcriben de los GRC de trabajo. Las cifras derivadas se identifican como cálculos; la tabla no afirma que los flujos se hayan ejecutado.

## Simulación S3 QPSK

| Variable | Valor | Procedencia o relación |
|---|---:|---|
| Orden QPSK | 4 | Tabla del bloque Chunks to Symbols |
| Mapeo | 00→1, 01→j, 10→−1, 11→−j | Orden de la tabla del GRC, MSB primero |
| Tasa de símbolos `Rs` | 32 ksym/s | Variable del GRC |
| Bits por símbolo | 2 | QPSK |
| Tasa de bits `Rb` | 64 kbit/s | Derivada: `2 Rs` |
| Muestras por símbolo `SPS` | 8 | Variable del GRC |
| Tasa de muestreo `fs` | 256 kS/s | Derivada: `Rs × SPS` |
| Retardo del eco | 8 muestras = 1 símbolo = 31,25 µs | Índice del tap y `8/fs` |
| Ganancia directa | 1 | Tap de índice 0 |
| Ruido del Channel Model | 0,05 | `noise_voltage` / `noise_amp` declarada en el GRC |
| Interpolación | `h=[1]*SPS` | Pulso rectangular declarado |

El vector de taps implementa `[1, 0, 0, 0, 0, 0, 0, 0, c]`, donde `c = eco_real + j·eco_imag`. Los cuatro controles son:

| Condición | `eco_real` | `eco_imag` | `|c|` calculado | Fase calculada |
|---|---:|---:|---:|---:|
| Referencia | 0,00 | 0,00 | 0 | 0° |
| Suave | 0,20 | 0,05 | 0,2062 | 14,04° |
| Media (predeterminada) | 0,35 | 0,15 | 0,3808 | 23,20° |
| Fuerte | 0,50 | 0,20 | 0,5385 | 21,80° |

## Enlace físico SDR de imagen

| Parámetro declarado | TX | RX |
|---|---:|---:|
| Modulación | 16-QAM, `Es=1` | Decisión 16-QAM |
| `Rs` / `Rb` / `SPS` | 8 ksym/s / 32 kbit/s / 8 | Valores compatibles declarados |
| Tasa base / tasa de radio | 64 kS/s / 2 MS/s | 64 kS/s / 2 MS/s |
| Filtro RRC | β=0,5, span=11 | β=0,5, span=11 |
| Frecuencia central / offset | 960 MHz / 200 kHz | Variables del GRC RX |
| Ganancias | `tx_amp=0,15`, `tx_vga=20` | `rx_lna=16`, `rx_vga=20` |
| AWGN digital inicial | 0 | — |

Los valores SDR describen la configuración guardada en los archivos, no una lectura verificada del video ni una medición del equipo durante la práctica. Consulte `PRACTICAS_SDR.md` antes de interpretar el alcance de los registros disponibles.
