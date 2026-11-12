# Alcance de la Guía 4 y BER

La Guía 4 recibida plantea instrumentar una curva BER frente a `Eb/N0` con bloques y scripts de ejemplo. Los scripts incluidos (`e_BER_Curve.py` y `e_EbN0_Sweep.py`) coinciden con bloques incrustados en el material GRC de referencia; esa plantilla no está integrada en los flujos S3 ni en el enlace SDR de imagen.

En los materiales revisados no hay una curva BER experimental ni un CSV de mediciones. El flujo S3 no incluye receptor digital, comparación de bits o medidor BER. Los registros de la práctica SDR de imagen no demuestran por sí mismos una medida `Eb/N0` ni una tasa de error.

Por alcance, este proyecto conserva la propuesta y sus archivos en `organizar/Fase4/`, sin conectar los scripts a los flujos, generar CSV de BER, afirmar resultados o presentar la propuesta como una actividad ejecutada. Cualquier estudio futuro debe documentar sincronización, definición de bits comparados, `Eb/N0`, longitud de muestra y condiciones de repetición antes de reportar una curva.
