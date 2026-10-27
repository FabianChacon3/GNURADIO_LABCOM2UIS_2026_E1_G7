#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caracteriza audio y visualiza forma de onda, espectro y espectrograma.

Uso:
    python src/caracterizar_audio.py data/entrada/audio_demo.wav
    python src/caracterizar_audio.py cancion.mp3 --guardar-graficas

Dependencias: numpy, matplotlib, soundfile. Para MP3, soundfile necesita una
compilación con soporte MPEG; si no lo tiene, convierte primero con FFmpeg:
ffmpeg -i cancion.mp3 -ac 1 -ar 44100 -c:a pcm_s16le audio_demo.wav
"""
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt


def load_audio(path):
    try:
        import soundfile as sf
        audio, sr = sf.read(path, always_2d=True, dtype='float64')
        subtype = sf.info(path).subtype
        channels = audio.shape[1]
        return audio, int(sr), subtype, channels
    except Exception as first_error:
        # Fallback para WAV PCM cuando soundfile no puede leer el archivo.
        try:
            from scipy.io import wavfile
            sr, raw = wavfile.read(path)
            subtype = str(raw.dtype)
            if raw.ndim == 1:
                raw = raw[:, None]
            if np.issubdtype(raw.dtype, np.integer):
                info = np.iinfo(raw.dtype)
                scale = max(abs(info.min), abs(info.max))
                audio = raw.astype(np.float64) / scale
            else:
                audio = raw.astype(np.float64)
            return audio, int(sr), subtype, audio.shape[1]
        except Exception as second_error:
            raise RuntimeError(
                f"No pude leer el archivo. Error soundfile: {first_error}. "
                f"Error WAV fallback: {second_error}. Para MP3, instala soporte MP3 "
                "en soundfile o convierte a WAV PCM con FFmpeg."
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archivo', help='Ruta al audio WAV/FLAC/AIFF o MP3 compatible')
    parser.add_argument('--guardar-graficas', action='store_true', help='Guarda PNG en data/evidencia/')
    parser.add_argument('--salida', help='Ruta explícita del PNG generado')
    parser.add_argument('--max-segundos', type=float, default=10.0,
                        help='Duración mostrada en forma de onda (default: 10 s)')
    args = parser.parse_args()
    if not os.path.isfile(args.archivo):
        sys.exit(f"No existe el archivo: {args.archivo}")

    audio, sr, subtype, channels = load_audio(args.archivo)
    n, _ = audio.shape
    duration = n / sr
    peak = float(np.max(np.abs(audio))) if n else 0.0
    rms = float(np.sqrt(np.mean(audio ** 2))) if n else 0.0
    peak_dbfs = 20 * np.log10(peak) if peak > 0 else -np.inf
    rms_dbfs = 20 * np.log10(rms) if rms > 0 else -np.inf
    print('\n=== CARACTERIZACIÓN DEL AUDIO ===')
    print(f'Archivo:              {os.path.abspath(args.archivo)}')
    print(f'Formato/subtipo:      {subtype}')
    print(f'Canales:              {channels}')
    print(f'Frecuencia muestreo:  {sr:,} Hz')
    print(f'Muestras por canal:   {n:,}')
    print(f'Duración:             {duration:.3f} s ({duration/60:.2f} min)')
    print(f'Nyquist:              {sr/2:,.1f} Hz')
    print(f'Pico:                 {peak:.6f} ({peak_dbfs:.2f} dBFS)')
    print(f'RMS:                  {rms:.6f} ({rms_dbfs:.2f} dBFS)')
    if sr != 44100:
        print(f'\nAVISO: el grafo actual está configurado a 44100 Hz, pero este archivo es de {sr} Hz.')
        print('Si se reproduce a 44100 muestras/s sin remuestrear, la duración y el tono cambiarán.')
        print(f'Factor de velocidad esperado: {44100/sr:.6f} (1.0 significa igual velocidad).')
    if channels > 1:
        print('Nota: el archivo es estéreo/multicanal; el grafo actual puede usar solo el primer canal.')
    if peak > 1.0:
        print('AVISO: hay muestras con magnitud > 1.0; revisa clipping/normalización en la cadena.')

    # Mezcla mono para el análisis, sin modificar el archivo.
    x = np.mean(audio, axis=1)
    view_n = min(n, max(1, int(args.max_segundos * sr)))
    t = np.arange(view_n) / sr
    # FFT sobre hasta 30 segundos, con ventana Hann y normalización relativa.
    fft_n = min(n, max(1, int(min(duration, 30.0) * sr)))
    xf = x[:fft_n]
    if fft_n > 1:
        win = np.hanning(fft_n)
        spec = np.abs(np.fft.rfft(xf * win))
        freqs = np.fft.rfftfreq(fft_n, 1 / sr)
        spec_db = 20 * np.log10(np.maximum(spec / max(np.max(spec), 1e-15), 1e-12))
    else:
        freqs, spec_db = np.array([0]), np.array([0])

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), constrained_layout=True)
    axes[0].plot(t, x[:view_n], linewidth=0.7)
    axes[0].set_title(f'Forma de onda (primeros {view_n/sr:.2f} s)')
    axes[0].set_xlabel('Tiempo (s)'); axes[0].set_ylabel('Amplitud normalizada'); axes[0].grid(True, alpha=.3)

    axes[1].plot(freqs, spec_db, linewidth=0.8)
    axes[1].set_title('Espectro de magnitud relativo (FFT con ventana Hann)')
    axes[1].set_xlabel('Frecuencia (Hz)'); axes[1].set_ylabel('Magnitud (dB respecto al pico)')
    axes[1].set_xlim(0, sr/2); axes[1].set_ylim(-120, 3); axes[1].grid(True, alpha=.3)

    # Espectrograma: espectro en el tiempo para reconocer transitorios y contenido variable.
    specgram_nfft = min(2048, max(256, n))
    axes[2].specgram(x, NFFT=specgram_nfft, Fs=sr, noverlap=None, scale='dB')
    axes[2].set_title('Espectrograma')
    axes[2].set_xlabel('Tiempo (s)'); axes[2].set_ylabel('Frecuencia (Hz)'); axes[2].set_ylim(0, sr/2)
    fig.suptitle(f'{os.path.basename(args.archivo)} — {sr} Hz, {channels} canal(es), {duration:.2f} s')

    if args.guardar_graficas:
        if args.salida:
            out = args.salida
        else:
            out = os.path.join('data', 'evidencia',
                               os.path.splitext(os.path.basename(args.archivo))[0] + '_analisis.png')
        os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
        fig.savefig(out, dpi=160)
        print(f'Gráficas guardadas en: {out}')
    plt.show()

if __name__ == '__main__':
    main()
