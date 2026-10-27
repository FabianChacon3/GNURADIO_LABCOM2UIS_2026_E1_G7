#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compara audio de referencia y audio grabado a la salida del receptor QPSK.

Ejemplo:
    python src/comparar_audio_rx.py data/entrada/audio_demo.wav \
        data/resultados/audio_rx_capture.wav --guardar

El script alinea por correlación a pequeña escala, compara el tramo común y
muestra medidas de nivel/fidelidad, FFT Welch y forma de onda.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import resample_poly
from fractions import Fraction


def read_mono(path: str):
    data, fs = sf.read(path, dtype='float64', always_2d=True)
    if data.size == 0:
        raise ValueError(f'Archivo vacío: {path}')
    # Repetimos la política de referencia del preparador: promedio de canales.
    return np.mean(data, axis=1), int(fs), sf.info(path)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


def db(x):
    return float(20*np.log10(x)) if x > 0 else float('-inf')


def align_by_lag(ref, rx, fs, max_lag_s=0.005):
    # Señales de estimación diezmadas para que el cálculo no sea costoso.
    ds = max(1, fs // 4000)
    a = ref[::ds]
    b = rx[::ds]
    if len(a) > fs * 10 // ds:
        a = a[:fs * 10 // ds]
    if len(b) > fs * 10 // ds:
        b = b[:fs * 10 // ds]
    # Correlación normalizada; se remueve DC para no sesgar el lag.
    a = a - np.mean(a)
    b = b - np.mean(b)
    corr = signal.correlate(b, a, mode='full', method='fft')
    lags = signal.correlation_lags(len(b), len(a), mode='full')
    max_lag_full = int(max_lag_s * fs)
    max_lag_decimated = int(np.ceil(max_lag_full / ds))
    mask = np.abs(lags) <= max_lag_decimated
    # No usar valor absoluto: la referencia y RX no deberían alinearse con
    # polaridad invertida solo por una correlación negativa grande.
    lag_coarse = int(lags[mask][np.argmax(corr[mask])]) * ds

    # Refinamiento en resolución de una muestra alrededor del lag grueso.
    # La correlación de música puede tener picos locales; se busca el mejor
    # coeficiente firmado sobre un tramo de hasta 5 s.
    nref = min(len(ref), len(rx), max(1, 5 * fs))
    radius = max(1, ds)
    candidates = range(max(-max_lag_full, lag_coarse-radius), min(max_lag_full, lag_coarse+radius)+1)
    best_lag, best_score = lag_coarse, -np.inf
    for lag in candidates:
        if lag >= 0:
            a, b = ref[:max(0, nref-lag)], rx[lag:lag+max(0, nref-lag)]
        else:
            a, b = ref[-lag:min(len(ref), -lag+nref)], rx[:min(len(rx), nref)]
            m = min(len(a), len(b)); a, b = a[:m], b[:m]
        m = min(len(a), len(b))
        if m < fs // 2:
            continue
        a = a[:m] - np.mean(a[:m]); b = b[:m] - np.mean(b[:m])
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        score = float(np.dot(a, b) / denom) if denom > 0 else -np.inf
        if score > best_score:
            best_score, best_lag = score, lag
    return int(best_lag)


def spectral_curve(x, fs, nperseg=8192):
    nperseg = min(nperseg, len(x))
    if nperseg < 16:
        return np.array([0.0]), np.array([-120.0]), np.array([0.0])
    f, pxx = signal.welch(x, fs=fs, window='hann', nperseg=nperseg, noverlap=nperseg//2, scaling='density')
    ref = np.max(pxx) if len(pxx) else 0
    dbrel = 10*np.log10(np.maximum(pxx / max(ref, 1e-30), 1e-12))
    total = np.sum(pxx)
    cdf = np.cumsum(pxx) / max(total, 1e-30)
    return f, dbrel, cdf


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('referencia', help='Audio esperado, recomendado audio_demo.wav ya preparado')
    p.add_argument('recibido', help='WAV guardado por el bloque Wav File Sink en la recepción')
    p.add_argument('--max-segundos', type=float, default=20.0, help='Duración máxima comparada (default 20 s)')
    p.add_argument('--ventana-ms', type=float, default=40.0, help='Ventana temporal para gráfica de forma (default 40 ms)')
    p.add_argument('--guardar', action='store_true', help='Guarda PNG y JSON junto al WAV recibido')
    p.add_argument('--salida-dir', default='data/resultados',
                   help='Directorio para PNG y JSON generados (default: data/resultados)')
    p.add_argument('--sin-alinear', action='store_true', help='No estima ni corrige retardo temporal')
    args = p.parse_args()
    for fn in (args.referencia, args.recibido):
        if not Path(fn).is_file():
            p.error(f'No existe el archivo: {fn}')

    try:
        ref, fs_ref, info_ref = read_mono(args.referencia)
        rx, fs_rx, info_rx = read_mono(args.recibido)
    except Exception as e:
        p.error(str(e))

    warnings = []
    if fs_rx != fs_ref:
        warnings.append(f'Frecuencias distintas ({fs_ref} Hz ref, {fs_rx} Hz RX); se remuestreó RX en memoria para comparar, pero revise el grafo.')
        ratio = Fraction(fs_ref, fs_rx).limit_denominator(100000)
        rx = resample_poly(rx, ratio.numerator, ratio.denominator)
        fs_rx = fs_ref

    lag = 0 if args.sin_alinear else align_by_lag(ref, rx, fs_ref)
    # lag > 0 significa que RX está retrasado respecto a referencia.
    if lag > 0:
        rx_aligned, ref_aligned = rx[lag:], ref[:len(rx)-lag]
    elif lag < 0:
        ref_aligned, rx_aligned = ref[-lag:], rx[:len(ref)+lag]
    else:
        ref_aligned, rx_aligned = ref, rx
    n = min(len(ref_aligned), len(rx_aligned), max(1, int(args.max_segundos*fs_ref)))
    ref_aligned = ref_aligned[:n]
    rx_aligned = rx_aligned[:n]
    if n < fs_ref:
        warnings.append('El tramo común dura menos de 1 segundo; las métricas pueden ser poco estables.')

    # Métricas sin ajustes de nivel y después de ajustar solamente un factor
    # escalar, para separar pérdida de amplitud de distorsión/errores.
    error = ref_aligned - rx_aligned
    mse = float(np.mean(error**2))
    raw_snr = 10*np.log10(np.sum(ref_aligned**2) / max(np.sum(error**2), 1e-30))
    corr = float(np.corrcoef(ref_aligned, rx_aligned)[0, 1]) if np.std(ref_aligned)>0 and np.std(rx_aligned)>0 else float('nan')
    denominator = float(np.dot(rx_aligned, rx_aligned))
    gain_fit = float(np.dot(ref_aligned, rx_aligned) / denominator) if denominator > 0 else 0.0
    rx_fit = rx_aligned * gain_fit
    err_fit = ref_aligned - rx_fit
    snr_fit = 10*np.log10(np.sum(ref_aligned**2) / max(np.sum(err_fit**2), 1e-30))
    peak_ref, peak_rx = float(np.max(np.abs(ref_aligned))), float(np.max(np.abs(rx_aligned)))
    clipping_rx = float(np.mean(np.abs(rx_aligned) >= 0.999)) * 100
    f_ref, s_ref, cdf_ref = spectral_curve(ref_aligned, fs_ref)
    f_rx, s_rx, cdf_rx = spectral_curve(rx_aligned, fs_ref)
    bw95_ref = float(f_ref[min(np.searchsorted(cdf_ref, .95), len(f_ref)-1)])
    bw99_ref = float(f_ref[min(np.searchsorted(cdf_ref, .99), len(f_ref)-1)])
    bw95_rx = float(f_rx[min(np.searchsorted(cdf_rx, .95), len(f_rx)-1)])
    bw99_rx = float(f_rx[min(np.searchsorted(cdf_rx, .99), len(f_rx)-1)])

    print('\n=== COMPARACIÓN DE AUDIO: REFERENCIA vs RX ===')
    print(f'Referencia:                  {Path(args.referencia).resolve()}')
    print(f'Recibido:                    {Path(args.recibido).resolve()}')
    print(f'Referencia metadata:         {info_ref.samplerate} Hz, {info_ref.channels} canal(es), {info_ref.subtype}, {info_ref.duration:.3f} s')
    print(f'Recibido metadata:           {info_rx.samplerate} Hz, {info_rx.channels} canal(es), {info_rx.subtype}, {info_rx.duration:.3f} s')
    print(f'Retardo estimado corregido:  {lag/fs_ref*1000:.3f} ms')
    print(f'Duración común analizada:    {n/fs_ref:.3f} s')
    print(f'RMS ref / RX:                {rms(ref_aligned):.6f} / {rms(rx_aligned):.6f}')
    print(f'Pico ref / RX:               {peak_ref:.6f} / {peak_rx:.6f}')
    print(f'Error cuadrático medio MSE:  {mse:.8e}')
    print(f'Correlación temporal:        {corr:.6f}')
    print(f'SNR de reconstrucción cruda: {raw_snr:.2f} dB')
    print(f'Ganancia óptima RX->ref:     {gain_fit:.6f}x ({db(abs(gain_fit)):.2f} dB)')
    print(f'SNR tras ajuste de nivel:    {snr_fit:.2f} dB')
    print(f'Muestras RX cerca de clipping: {clipping_rx:.4f} %')
    print(f'Ancho banda 95% energía ref/RX: {bw95_ref:.0f} / {bw95_rx:.0f} Hz')
    print(f'Ancho banda 99% energía ref/RX: {bw99_ref:.0f} / {bw99_rx:.0f} Hz')
    for w in warnings:
        print('AVISO: ' + w)
    print('Interpretación: SNR cruda incluye diferencias de volumen; SNR ajustada separa parcialmente el error de nivel. Ninguna métrica por sí sola describe toda la calidad perceptual.')

    # Gráficas: forma de onda corta, espectro relativo y residuo.
    nview = min(n, max(10, int(args.ventana_ms*1e-3*fs_ref)))
    t = np.arange(nview)/fs_ref
    residual = ref_aligned[:nview] - rx_aligned[:nview]
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), constrained_layout=True)
    axes[0].plot(t*1000, ref_aligned[:nview], label='Referencia', linewidth=.9)
    axes[0].plot(t*1000, rx_aligned[:nview], label='Recibido', linewidth=.8, alpha=.8)
    axes[0].set_title(f'Forma de onda alineada — primeros {nview/fs_ref*1000:.1f} ms')
    axes[0].set_xlabel('Tiempo (ms)'); axes[0].set_ylabel('Amplitud'); axes[0].grid(True, alpha=.3); axes[0].legend()
    axes[1].plot(f_ref, s_ref, label='Referencia', linewidth=1.0)
    axes[1].plot(f_rx, s_rx, label='Recibido', linewidth=1.0, alpha=.85)
    axes[1].set_xlim(0, fs_ref/2); axes[1].set_ylim(-100, 3)
    axes[1].set_title('Densidad espectral de potencia relativa (Welch, normalizada por separado)')
    axes[1].set_xlabel('Frecuencia (Hz)'); axes[1].set_ylabel('Nivel relativo (dB)'); axes[1].grid(True, alpha=.3); axes[1].legend()
    axes[2].plot(t*1000, residual, linewidth=.8)
    axes[2].set_title('Error temporal: referencia − recibido')
    axes[2].set_xlabel('Tiempo (ms)'); axes[2].set_ylabel('Error de amplitud'); axes[2].grid(True, alpha=.3)
    fig.suptitle(f'Comparación QPSK — correlación {corr:.3f}, SNR cruda {raw_snr:.1f} dB, ajustada {snr_fit:.1f} dB')
    if args.guardar:
        output_dir = Path(args.salida_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / Path(args.recibido).stem
        png = str(out) + '_comparacion.png'
        js = str(out) + '_metricas.json'
        fig.savefig(png, dpi=160)
        report = {
            'reference': str(Path(args.referencia).resolve()), 'received': str(Path(args.recibido).resolve()),
            'fs_hz': fs_ref, 'analyzed_duration_s': n/fs_ref, 'alignment_lag_ms': lag/fs_ref*1000,
            'rms_reference': rms(ref_aligned), 'rms_received': rms(rx_aligned), 'peak_reference': peak_ref,
            'peak_received': peak_rx, 'mse': mse, 'correlation': corr, 'snr_raw_db': float(raw_snr),
            'fitted_rx_to_ref_gain': gain_fit, 'snr_after_gain_fit_db': float(snr_fit),
            'clipping_rx_percent': clipping_rx, 'bandwidth_95_percent_reference_hz': bw95_ref,
            'bandwidth_95_percent_received_hz': bw95_rx, 'bandwidth_99_percent_reference_hz': bw99_ref,
            'bandwidth_99_percent_received_hz': bw99_rx, 'warnings': warnings,
        }
        Path(js).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'Gráfica guardada: {png}')
        print(f'Métricas JSON:    {js}')
    plt.show()

if __name__ == '__main__':
    main()
