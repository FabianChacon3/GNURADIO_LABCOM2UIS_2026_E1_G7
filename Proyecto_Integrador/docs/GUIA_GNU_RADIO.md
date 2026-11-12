# Guía de uso de GNU Radio Companion

Esta guía describe cómo abrir y comprender las copias de trabajo del caso S3 y de los flujos SDR de imagen. Las fuentes recibidas permanecen en organizar/. Los flujogramas de este proyecto se revisaron estáticamente; no se pudieron ejecutar en este entorno porque no tiene GNU Radio Companion, GNU Radio, PyQt5 ni HackRF.

## 1. Caso S3: canal QPSK con multitrayectoria

Archivo: ../src/s3/Enlace_S3_Multitrayectoria_Grupo3.grc

1. Abra GNU Radio Companion y seleccione el archivo indicado.
2. Revise primero la tabla de constelación, las variables de tasa y el vector taps_canal.
3. Ejecute el flujo desde GRC. La fuente aleatoria genera bits; Pack K Bits y Packed to Unpacked preparan grupos de dos bits; Chunks to Symbols usa el orden QPSK del GRC; el interpolador produce pulsos rectangulares a SPS=8.
4. El bloque Channel Model añade AWGN y aplica el camino directo junto con el eco retardado. La salida se conecta a los visores de constelación, frecuencia y tiempo.
5. Cambie solo eco_real y eco_imag entre las cuatro pruebas. Mantenga constantes noise_amp=0.05, Rs, SPS, la tabla QPSK y las escalas de los visores.
6. Detenga el flujo antes de cambiar la condición y registre los valores utilizados si captura pantallas.

### Mapeo y valores

El orden de la tabla conservado del GRC es:

| Grupo de dos bits (MSB primero) | Símbolo complejo |
|---|---:|
| 00 | 1+0j |
| 01 | 0+1j |
| 10 | -1+0j |
| 11 | 0-1j |

| Prueba | eco_real | eco_imag | Último tap del canal |
|---|---:|---:|---:|
| Referencia | 0.00 | 0.00 | 0j |
| Suave | 0.20 | 0.05 | 0.20+0.05j |
| Media | 0.35 | 0.15 | 0.35+0.15j |
| Fuerte | 0.50 | 0.20 | 0.50+0.20j |

El vector de taps coloca el camino directo en la muestra 0 y el eco en la muestra 8. Como SPS=8, el retardo es un símbolo: 8/256000 s = 1/32000 s = 31,25 µs. Las tasas son Rs=32 ksym/s, Rb=64 kbit/s, SPS=8 y fs=Rs×SPS=256 kS/s.

### Lectura correcta de los visores

- **Tiempo:** muestra I y Q de la señal compleja después del canal.
- **Constelación:** recibe todas las muestras del flujo interpolado; incluye las muestras de cada pulso rectangular. No es una salida de símbolos decididos por un receptor.
- **Frecuencia:** muestra el espectro de salida con eje vertical de ganancia relativa en dB. El rótulo evita llamarlo PSD calibrada.

Este flujo no tiene receptor digital ni medidor BER. No use la dispersión del visor para afirmar una BER medida.

## 2. Transmisión y recepción SDR de imágenes

Los flujos TX y RX son independientes y se ejecutan en computadores/radios que deben tener una configuración compatible. No son el modelo S3 de multitrayectoria.

### Transmisor

Archivo: ../src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc

- El TX lee assets/Logouis.png, la convierte a 160×80 RGB y crea tramas con preámbulo de 64 símbolos, cabecera, payload de hasta 128 bytes, CRC32 y guarda de 24 símbolos.
- Los bytes se separan en nibbles y se mapean a 16-QAM. El flujo se conforma con RRC, escala la señal, suma el AWGN digital configurado (inicialmente cero), remuestrea de 64 kS/s a 2 MS/s y llega al sink HackRF.
- Los valores declarados incluyen Rs=8 ksym/s, SPS=8, Rb=32 kbit/s, beta RRC=0.5 y radio_rate=2 MS/s. La frecuencia y ganancias configuradas en el GRC son parámetros de ese archivo, no valores medidos durante la práctica.
- Si el recurso de entrada no se encuentra, el bloque original contiene una ruta de respaldo que genera una imagen de prueba. Verifique en la salida que se cargó el archivo esperado antes de interpretar una transmisión como envío del logo UIS.

### Receptor

Archivo: ../src/sdr_imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc

- La entrada HackRF se desplaza digitalmente y se remuestrea de 2 MS/s a 64 kS/s.
- La cadena aplica control de ganancia, seguimiento de frecuencia, sincronización de reloj con filtro RRC y decisión de símbolos 16-QAM.
- El bloque de imagen busca el preámbulo, prueba cuatro rotaciones de fase, recupera bytes, valida CRC32, reúne los paquetes y declara guardar el resultado en data/resultados/rx_imagen.png.
- Los sinks de registro conectados escriben muestras complejas y decisiones de símbolo bajo data/resultados/. Desactívelos en GRC si no necesita esas capturas, para evitar archivos grandes.
- La carpeta de salida está incluida en el árbol del proyecto. El PNG solo demuestra reconstrucción si aparece tras recibir todas las tramas; el código estático y un mensaje de progreso no bastan para afirmar que la imagen final fue verificada.

Los GRC mencionan HackRF y frecuencias de operación; el uso de hardware requiere la configuración real del laboratorio. Esta guía no establece parámetros RF distintos a los declarados por los archivos ni afirma una ejecución realizada.

## 3. Guía 4

La carpeta ../../organizar/Fase4/ conserva la propuesta de instrumentación BER vs. Eb/N0 y sus scripts de referencia. No conecte esa plantilla a los flujos TX/RX de este proyecto ni genere una curva/CSV: la práctica documentada aquí fue la validación de los flujogramas y no la medición BER experimental de Guía 4.

## 4. Estado de verificación

Los GRC de trabajo se pueden analizar como YAML y no muestran conexiones hacia nombres de bloque inexistentes. Este chequeo no valida puertos/tipos frente a GNU Radio ni sustituye abrir, generar y ejecutar cada flujo. Para la validación de hardware se necesita GNU Radio con los módulos correspondientes, HackRF disponibles y una prueba manual en el entorno de laboratorio.
