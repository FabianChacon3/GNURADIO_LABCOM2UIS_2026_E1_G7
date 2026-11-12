# Prácticas SDR y transmisión de imágenes

## Enlace de clase

Los videos suministrados muestran trabajo con transmisor y receptor SDR en computadores distintos. El video `organizar/transmisor.mp4` muestra el flujo TX y el hardware; `organizar/receptoryvalidacionpalabra.mp4` muestra el flujo RX y visualizaciones temporales y de constelación. Los archivos se enlazan desde el blog y no se duplican en el proyecto.

Los archivos `src/sdr_imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc` y `LAB_RX_16QAM_HackRF_IMAGEN.grc` describen una variante de 16-QAM para transmitir una imagen. Son flujos separados del modelo S3 QPSK. Los parámetros declarados se resumen en `PARAMETROS.md`; no se puede asegurar que cada valor coincida con la sesión grabada.

## Trama de imagen

El transmisor carga `src/sdr_imagen/assets/Logouis.png`, la convierte a RGB de 160×80 y serializa la imagen en paquetes de hasta 128 bytes. Cada paquete incorpora cabecera, preámbulo, blanqueo y CRC32; dos nibbles de cada byte se mapean en símbolos 16-QAM. El flujo de muestras se conforma con RRC y se adapta a la tasa de radio.

El receptor sincroniza con el preámbulo, prueba cuatro rotaciones de fase, recupera los bytes y valida el CRC. Después reensambla los paquetes y declara escribir `src/sdr_imagen/data/resultados/rx_imagen.png`. No se encontró ese archivo entre las evidencias recibidas. `organizar/Imagenrecibida.jpeg` es una captura de pantalla con registros, no el PNG reconstruido. Por eso el código documenta el procedimiento, pero no prueba la reconstrucción final.

## Uso

Abra cada GRC en GNU Radio Companion por separado y compruebe las dependencias de HackRF y los bloques OOT disponibles. Use configuraciones RF autorizadas para el laboratorio y verifique que TX y RX compartan tasas, frecuencia, formato de trama y parámetros de sincronización. Revise `GUIA_GNU_RADIO.md` para las rutas y advertencias sobre registros. La inspección estática no reemplaza una prueba TX/RX con hardware.

La actividad SDR es una experiencia complementaria de comunicación física; no es una prueba de la respuesta de multitrayectoria S3 ni genera una curva BER.
