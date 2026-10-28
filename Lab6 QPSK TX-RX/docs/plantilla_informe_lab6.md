# Laboratorio 6: Transmisión y recepción digital de audio QPSK

**Integrantes:** [nombres]  
**Asignatura / grupo:** [datos]  
**Fecha:** [fecha]  
**Repositorio:** [URL/commit/tag]

## 1. Objetivos

[Explicar qué se busca comprobar al modificar el nivel relativo de TX y el ruido del canal, y al comparar audio de referencia con audio reconstruido.]

## 2. Fundamento teórico

### 2.1 Muestreo y frecuencia de Nyquist

[Definir la frecuencia de muestreo, el límite de Nyquist y por qué el remuestreo de 48 kHz a 44,1 kHz debe transformar las muestras.]

### 2.2 Cuantización PCM y conversión de bits

[Documentar que el grafo actual convierte audio float a byte con escala 128 antes de transmitirlo. Explicar la limitación de resolución efectiva de 8 bits.]

### 2.3 Modulación QPSK y canal con ruido

[Explicar 2 bits/símbolo, los puntos de la constelación, la ganancia TX relativa, ruido aditivo y SNR.]

## 3. Herramientas y datos

| Elemento | Valor utilizado |
|---|---|
| Sistema operativo | [ ] |
| GNU Radio Companion | [versión exacta] |
| Python | [versión] |
| Archivo fuente y procedencia/licencia | [ ] |
| Fs fuente / canales / formato | [ ] |
| Fs procesada / canales / formato | [ ] |
| Pico y RMS del audio procesado | [ ] |

## 4. Preparación del audio

[Comando de `lab6_audio.py --solo-preparar`, decisiones de downmix y normalización. Incluir la gráfica de caracterización del archivo original y del preparado.]

## 5. Arquitectura implementada

[Insertar captura del flujo GRC. Identificar: fuente WAV, cuantización, empaquetado, mapeo QPSK, interpolación, ganancia TX, sumador de ruido, decimación, decisor, reconstrucción, audio sink y captura WAV.]

Parámetros derivados:

- Fs audio: 44.100 muestras/s.
- Bits por muestra antes de modulación: 8.
- Símbolos QPSK por muestra: 4.
- `Sps`: 8.
- Tasa de símbolos estimada: 176.400 símbolos/s.
- Tasa compleja del canal: 1.411.200 muestras/s. La guía puede sugerir 1,024
  MHz, pero ese valor no coincide con la configuración actual del `.grc`;
  reportar la discrepancia en lugar de ocultarla.

## 6. Metodología experimental

[Indicar cómo se detuvo y guardó cada captura, qué variables se mantuvieron fijas y qué variable se modificó en cada comparación.]

| Caso | `tx_power_db` (dB) | `noise_amp` | `rx_gain` | `scale` | Nombre de captura |
|---|---:|---:|---:|---:|---|
| A: base ideal | 0 | 0,00 | 1,0 | 128 | [ ] |
| B: ruido leve | 0 | 0,02 | 1,0 | 128 | [ ] |
| C: TX reducido | -6 | 0,02 | 1,0 | 128 | [ ] |
| D: TX bajo | -12 | 0,02 | 1,0 | 128 | [ ] |
| E: más ruido | 0 | 0,05 | 1,0 | 128 | [ ] |

## 7. Resultados

Incluir las figuras de la forma de onda, espectro del audio, espectro del canal y constelación recibida. No confundir el espectro del archivo musical con el espectro de la señal QPSK de banda base.

| Caso | TX (dB) | Ruido | RX gain | Escala | Sps | Duración (s) | Correlación | MSE | SNR cruda (dB) | SNR ajustada (dB) | BW 95% RX (Hz) | Observación auditiva |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | | | | | | | | | | | | |
| B | | | | | | | | | | | | |
| C | | | | | | | | | | | | |
| D | | | | | | | | | | | | |
| E | | | | | | | | | | | | |

## 8. Análisis y discusión

- ¿Cómo cambia la constelación al reducir el nivel TX con ruido fijo?
- ¿Cómo cambia el audio recibido al aumentar `noise_amp` manteniendo TX fijo?
- ¿El cambio que se escucha es de volumen, de tono/velocidad o de distorsión por errores?
- ¿Qué parte de la diferencia se explica por cuantización a 8 bits?
- ¿Cómo varían correlación, MSE y SNR de reconstrucción entre escenarios?
- ¿Qué indica el ancho de banda acumulado y qué no permite concluir?

Advertencia: SNR de reconstrucción de audio no es igual a SNR del canal y el
script de comparación no mide BER directamente. Las filas deben completarse
solo con capturas realmente ejecutadas y con sus parámetros registrados.

## 9. Limitaciones

[Documentar: audio convertido a mono, cuantización de 8 bits, modelo simplificado de canal, ausencia de sincronización/filtrado de conformación/FEC y falta de medida directa de BER.]

## 10. Conclusiones

[Conclusiones sustentadas en los resultados; distinguir hechos medidos de expectativas teóricas.]

## 11. Reproducibilidad

- Commit/tag del repositorio: [ ]
- Comando de preparación: [ ]
- Comandos de análisis/comparación: [ ]
- Versiones de software: [ ]
- Ubicación de resultados/figuras: [ ]
