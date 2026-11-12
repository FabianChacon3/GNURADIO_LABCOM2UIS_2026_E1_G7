# Bitácora de modificaciones

## Alcance

Las fuentes recibidas en `organizar/` se conservaron. Las correcciones se aplicaron a copias dentro de `Proyecto_Integrador/`. Esta bitácora separa la inspección estática, los cálculos analíticos y las actividades cuya ejecución requiere GNU Radio o hardware.

## Cambios

| Elemento | Acción | Estado |
|---|---|---|
| GRC S3 | Copia de trabajo con comentarios de bloques y rótulo de espectro relativo, conservando el flujo y sus valores | Revisado como YAML; ejecución GNU Radio pendiente |
| GRC TX/RX de imagen | Copias de trabajo con rutas relativas al proyecto para el logo, los registros y la imagen recibida | Revisado estáticamente; prueba con HackRF pendiente |
| GRC TX/RX anteriores | Copias identificadas en `src/sdr_imagen/originales/` para comparar el flujo previo de texto conocido | Conservadas sin integrarlas como práctica de imagen |
| Análisis S3 | Nuevo `src/s3/analizar_s3.py` para respuesta impulsional, respuesta frecuencial, constelaciones y secuencia temporal deterministas | Ejecutado; PNG y CSV etiquetados como modelo analítico |
| Blog | Copia de `organizar/BLOG_ABET_FINAL.html`, actualizada con parámetros S3, figuras y práctica SDR; conserva diagramas, estilos e interacción | Revisión de enlaces y script descrita en el informe final |
| Documentación | Guías de GNU Radio, parámetros, prácticas SDR, figuras, referencias y alcance de Guía 4 | Preparada a partir de los archivos disponibles |

## Límites de validación

- Los archivos GRC se revisaron como YAML y se comprobaron las referencias de conexiones. No se generaron ni ejecutaron con GNU Radio Companion en este entorno.
- El script analítico se ejecutó con Python. Sus salidas no son capturas de GNU Radio, mediciones RF, PSD calibradas ni estimaciones BER.
- Los videos se inspeccionaron visualmente. No permiten confirmar por sí solos todos los parámetros de los GRC ni demostrar la recepción de un PNG reconstruido.
- La propuesta de instrumentación BER de Guía 4 se conserva como material de referencia; no se implementó ni se simularon sus resultados.
