# Script y figuras del modelo S3

## Reproducción

Desde la carpeta `Proyecto_Integrador/`, ejecute:

```bash
python src/s3/analizar_s3.py
```

El script usa NumPy y Matplotlib y escribe las salidas en `data/figuras/s3/`. Cada PNG tiene un CSV de datos asociado:

| Salida | Contenido |
|---|---|
| `s3_respuesta_impulsional_modelo.png/.csv` | Tap directo y eco complejo en n=0 y n=8 para cuatro condiciones |
| `s3_respuesta_frecuencial_modelo.png/.csv` | `|H(f)|` y magnitud en dB calculadas a partir de los taps |
| `s3_constelaciones_modelo.png/.csv` | Símbolo actual más eco de un símbolo previo, para QPSK cardinal |
| `s3_secuencia_temporal_modelo.png/.csv` | Secuencia QPSK determinista y su salida a tasa de símbolo |

## Modelo y alcance

Para `c=eco_real+j·eco_imag` y un retardo de un símbolo, el cálculo es `y[k]=x[k]+c·x[k−1]`. La respuesta frecuencial normalizada es `H(u)=1+c·exp(−j2πu)`, donde `u=f/Rs`, y `|H(u)|²=1+|c|²+2(eco_real·cos(2πu)+eco_imag·sin(2πu))`.

El script utiliza símbolos deterministas y no añade ruido. Las figuras son una predicción analítica del modelo simplificado, no salidas del Channel Model, capturas del GRC, PSD calibradas ni mediciones de BER. El GRC S3, en cambio, declara ruido `0,05` y usa pulsos rectangulares a 8 SPS. Para comprobar sus visores es necesario ejecutar el flujo en GNU Radio.
