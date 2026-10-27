#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara audio de entrada para el laboratorio GNU Radio QPSK.

Convierte a mono PCM de 16 bits y remuestrea con un filtro polifásico real.
Por defecto normaliza el pico a -1 dBFS para que la cuantización de 8 bits que
usa el flujo original aproveche mejor su rango dinámico. Use --sin-normalizar
si necesita conservar exactamente la amplitud relativa de la fuente.

Ejemplo:
    python src/preparar_audio.py cancion.wav
    python src/preparar_audio.py cancion.wav --salida data/entrada/audio_demo.wav --sin-normalizar
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from fractions import Fraction


def dbfs(x: float) -> float:
    return float(20 * np.log10(x)) if x > 0 else float('-inf')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('entrada', help='Archivo de audio de origen (WAV/FLAC/AIFF y otros formatos admitidos por libsndfile)')
    p.add_argument('--salida', default='data/entrada/audio_demo.wav',
                   help='WAV mono PCM16 de salida (default: data/entrada/audio_demo.wav)')
    p.add_argument('--fs', type=int, default=44100, help='Frecuencia de muestreo destino (default: 44100 Hz)')
    p.add_argument('--sin-normalizar', action='store_true', help='No cambia la amplitud pico; útil para conservar el nivel de la fuente')
    p.add_argument('--pico-dbfs', type=float, default=-1.0, help='Pico de normalización en dBFS cuando está habilitada (default: -1 dBFS)')
    args = p.parse_args()

    src, dst = Path(args.entrada), Path(args.salida)
    if not src.is_file():
        p.error(f'No existe el archivo de entrada: {src}')
    if src.resolve() == dst.resolve():
        p.error('La entrada y la salida no pueden ser el mismo archivo; conserva una copia maestra inmutable.')
    if args.fs <= 0:
        p.error('--fs debe ser un entero positivo')
    try:
        x, fs_in = sf.read(str(src), dtype='float64', always_2d=True)
    except Exception as e:
        p.error(f'No se pudo leer {src}: {e}. Si es MP3, conviértalo primero con FFmpeg a WAV/PCM.')

    if x.size == 0 or not np.isfinite(x).all():
        p.error('El archivo está vacío o contiene valores no finitos.')
    n_in, nchan_in = x.shape
    duration_in = n_in / fs_in
    peak_in = float(np.max(np.abs(x)))
    rms_in = float(np.sqrt(np.mean(x * x)))

    # Downmix determinista: media aritmética de canales. Puede cancelar parte
    # del contenido si L y R están en oposición de fase; se documenta en salida.
    mono = np.mean(x, axis=1)
    downmix_note = 'sin mezcla (entrada mono)' if nchan_in == 1 else 'mezcla mono por promedio aritmético de canales'

    # Conversión racional exacta, por ejemplo 48 kHz -> 44.1 kHz = 147/160.
    ratio = Fraction(args.fs, fs_in).limit_denominator(100000)
    if ratio.numerator * fs_in != ratio.denominator * args.fs:
        p.error('No se pudo representar la razón de remuestreo de forma exacta.')
    if fs_in != args.fs:
        y = resample_poly(mono, ratio.numerator, ratio.denominator)
    else:
        y = mono.copy()

    peak_pre_norm = float(np.max(np.abs(y))) if y.size else 0.0
    gain = 1.0
    if not args.sin_normalizar and peak_pre_norm > 0:
        target = 10 ** (args.pico_dbfs / 20.0)
        gain = target / peak_pre_norm
        y = y * gain
    peak_out = float(np.max(np.abs(y))) if y.size else 0.0

    # Protege PCM16 ante redondeo o material fuera de rango; clipping debe ser 0.
    clipped = int(np.count_nonzero(np.abs(y) > 1.0))
    if clipped:
        y = np.clip(y, -1.0, 1.0)

    dst.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dst), y, args.fs, subtype='PCM_16', format='WAV')
    info = sf.info(str(dst))

    print('\n=== PREPARACIÓN PARA GNU RADIO ===')
    print(f'Entrada:                  {src.resolve()}')
    print(f'Formato de entrada:       {sf.info(str(src)).format} / {sf.info(str(src)).subtype}')
    print(f'Frecuencia origen:        {fs_in:,} Hz')
    print(f'Canales origen:           {nchan_in}')
    print(f'Duración origen:          {duration_in:.3f} s')
    print(f'Pico/RMS origen:          {peak_in:.6f} ({dbfs(peak_in):.2f} dBFS) / {rms_in:.6f} ({dbfs(rms_in):.2f} dBFS)')
    print(f'Mezcla:                   {downmix_note}')
    print(f'Remuestreo:               {fs_in:,} -> {args.fs:,} Hz ({ratio.numerator}/{ratio.denominator})')
    print(f'Normalización:            {"desactivada" if args.sin_normalizar else f"pico objetivo {args.pico_dbfs:.2f} dBFS; ganancia aplicada {gain:.6f}x ({dbfs(gain):.2f} dB)"}')
    print(f'Pico salida:              {peak_out:.6f} ({dbfs(peak_out):.2f} dBFS)')
    print(f'Salida:                   {dst.resolve()}')
    print(f'Formato salida:           {info.format} / {info.subtype}; {info.channels} canal; {info.samplerate:,} Hz; {info.frames:,} muestras')
    print(f'Duración salida:          {info.duration:.3f} s')
    print(f'Nyquist salida:           {args.fs/2:,.1f} Hz')
    print('\nNOTA: remuestrear limita el contenido representable al nuevo Nyquist. La normalización cambia el nivel, no pretende recuperar bandas eliminadas por una codificación previa.')
    if nchan_in > 1:
        print('NOTA: el promedio L/R puede cancelar señal si los canales están casi en oposición de fase; escuche/verifique la mezcla mono antes del laboratorio.')
    if args.sin_normalizar and peak_out < 0.2:
        print('AVISO: la señal tiene pico bajo; con el cuantizador de 8 bits actual se aprovecharán pocos códigos. Considere usar la normalización para las pruebas de transmisión.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
