#!/usr/bin/env python3
"""Flujo único de preparación, caracterización y comparación de audio QPSK.

USO DESDE LA RAÍZ DEL LABORATORIO
=================================

1. Flujo completo (prepara, caracteriza y compara si existe una captura RX):

   python src/lab6_audio.py

2. Usar otra canción, sin importar su frecuencia o número de canales:

   python src/lab6_audio.py --entrada "ruta/a/otra_cancion.wav"

3. Solo preparar y generar las caracterizaciones, sin comparar RX:

   python src/lab6_audio.py --entrada "ruta/a/otra_cancion.wav" --solo-preparar

4. Comparar una captura específica y guardar los parámetros de la prueba:

   python src/lab6_audio.py ^
       --entrada data/entrada/audio_original.wav ^
       --recibido data/resultados/audio_rx_capture.wav ^
       --max-segundos 20 --tx-power-db 0 --noise-amp 0 ^
       --rx-gain 1 --scale 128 --sps 8

El audio original puede ser mono o estéreo y tener cualquier frecuencia de
muestreo compatible con soundfile. El script lee la frecuencia configurada
en el archivo .grc, convierte una copia a mono PCM16 y remuestrea esa copia
para que GNU Radio reciba el formato correcto. Nunca modifica el original.

SALIDAS
=======

data/entrada/audio_demo.wav
    Audio derivado que consume GNU Radio.
data/evidencia/audio_original_analisis.png
    Forma de onda, espectro y espectrograma de la fuente.
data/evidencia/audio_demo_analisis.png
    Las mismas caracterizaciones del audio preparado.
data/resultados/*_comparacion.png
    Comparación visual entre referencia y captura RX.
data/resultados/*_metricas.json
    Métricas, frecuencias detectadas, advertencias y parámetros del ensayo.

ORDEN DE TRABAJO CON GNU RADIO
==============================

1. Ejecuta este script con --solo-preparar o en modo completo.
2. Abre el archivo .grc y regenera QPSK_TX_RX.py desde GNU Radio Companion.
3. Ejecuta el flujo y espera a que Wav File Sink cierre la captura.
4. Ejecuta nuevamente este script para generar la comparación.

Las métricas de audio no son BER. La captura RX puede tener otra frecuencia:
el script la remuestrea en memoria para comparar y deja una advertencia en el
JSON. Para un resultado final, vuelve a capturar con el .grc vigente.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATA = ROOT / "data"
GRC = SRC / "lab6_tx_rx_audio_qpsk_mejorado.grc"


def read_audio(path: Path) -> tuple[np.ndarray, int, object]:
    """Lee un audio, convierte sus canales a mono y devuelve su frecuencia."""
    try:
        data, fs = sf.read(str(path), dtype="float64", always_2d=True)
    except Exception as exc:
        raise RuntimeError(f"No se pudo leer {path}: {exc}") from exc
    if data.size == 0 or not np.isfinite(data).all():
        raise ValueError(f"El archivo está vacío o contiene valores no finitos: {path}")
    return np.mean(data, axis=1), int(fs), sf.info(str(path))


def dbfs(value: float) -> float:
    return float(20 * np.log10(value)) if value > 0 else float("-inf")


def target_sample_rate() -> int:
    """Obtiene la frecuencia y valida las rutas configuradas en el GRC."""
    text = GRC.read_text(encoding="utf-8")
    match = re.search(
        r"- name: sample_rate_audio\s+id: variable.*?value: '(\d+)'",
        text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError("No se encontró sample_rate_audio en el archivo GRC.")
    paths = set(re.findall(r"file: (.+)", text))
    expected = {
        "../data/entrada/audio_demo.wav",
        "../data/resultados/audio_rx_capture.wav",
    }
    if not expected.issubset(paths):
        raise RuntimeError("Las rutas de entrada/salida del GRC no están organizadas.")
    return int(match.group(1))


def prepare_audio(source: Path, destination: Path, target_fs: int) -> None:
    """Crea el WAV derivado compatible con GNU Radio."""
    audio, fs_in, _ = read_audio(source)
    ratio = Fraction(target_fs, fs_in).limit_denominator(100000)
    if ratio.numerator * fs_in != ratio.denominator * target_fs:
        raise ValueError("No se pudo representar exactamente la razón de remuestreo.")
    if fs_in != target_fs:
        audio = resample_poly(audio, ratio.numerator, ratio.denominator)
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    gain = 10 ** (-1 / 20) / peak if peak > 0 else 1.0
    audio = audio * gain
    destination.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(destination), np.clip(audio, -1, 1), target_fs, subtype="PCM_16")
    print(
        f"Preparado: {source.name} ({fs_in:,} Hz) -> {destination} "
        f"(mono, {target_fs:,} Hz, PCM16, ganancia {gain:.6f}x)"
    )


def characterize(path: Path, output: Path, expected_fs: int) -> None:
    """Guarda forma de onda, espectro y espectrograma del audio."""
    audio, fs, info = read_audio(path)
    duration = len(audio) / fs
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio**2)))
    fft_n = min(len(audio), max(1, int(min(duration, 30) * fs)))
    sample = audio[:fft_n]
    window = np.hanning(fft_n) if fft_n > 1 else np.ones(fft_n)
    spectrum = np.abs(np.fft.rfft(sample * window))
    frequencies = np.fft.rfftfreq(fft_n, 1 / fs)
    spectrum_db = 20 * np.log10(np.maximum(spectrum / max(np.max(spectrum), 1e-15), 1e-12))
    view_n = min(len(audio), max(1, int(min(duration, 10) * fs)))
    time = np.arange(view_n) / fs
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), constrained_layout=True)
    axes[0].plot(time, audio[:view_n], linewidth=0.7)
    axes[0].set_title("Forma de onda")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("Amplitud")
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(frequencies, spectrum_db, linewidth=0.8)
    axes[1].set_title("Espectro relativo")
    axes[1].set_xlabel("Frecuencia (Hz)")
    axes[1].set_ylabel("dB respecto al pico")
    axes[1].set_xlim(0, fs / 2)
    axes[1].set_ylim(-120, 3)
    axes[1].grid(True, alpha=0.3)
    axes[2].specgram(audio, NFFT=min(2048, max(256, len(audio))), Fs=fs, scale="dB")
    axes[2].set_title("Espectrograma")
    axes[2].set_xlabel("Tiempo (s)")
    axes[2].set_ylabel("Frecuencia (Hz)")
    axes[2].set_ylim(0, fs / 2)
    fig.suptitle(f"{path.name} — {fs:,} Hz, {info.channels} canal(es), {duration:.2f} s")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(
        f"Caracterizado: {path.name} | {fs:,} Hz | {info.channels} canal(es) | "
        f"{duration:.3f} s | pico {peak:.6f} ({dbfs(peak):.2f} dBFS) | "
        f"RMS {rms:.6f} ({dbfs(rms):.2f} dBFS)"
    )
    if fs != expected_fs:
        print(f"  Aviso: este archivo tiene {fs} Hz; el flujo usa {expected_fs} Hz.")


def align(ref: np.ndarray, received: np.ndarray, fs: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Alinea referencia y RX mediante correlación en una ventana de 5 ms."""
    limit = min(len(ref), len(received), 10 * fs)
    a, b = ref[:limit], received[:limit]
    a -= np.mean(a)
    b -= np.mean(b)
    correlation = signal.correlate(b, a, mode="full", method="fft")
    lags = signal.correlation_lags(len(b), len(a), mode="full")
    allowed = np.abs(lags) <= int(0.005 * fs)
    lag = int(lags[allowed][np.argmax(correlation[allowed])])
    if lag > 0:
        return ref[:len(received) - lag], received[lag:], lag
    if lag < 0:
        return ref[-lag:], received[:len(ref) + lag], lag
    return ref, received, 0


def compare(reference: Path, received: Path, output_dir: Path, max_seconds: float, metadata: dict) -> None:
    """Calcula métricas y guarda la gráfica/JSON de comparación."""
    ref, fs_ref, ref_info = read_audio(reference)
    rx, fs_rx, rx_info = read_audio(received)
    warning = None
    if fs_rx != fs_ref:
        original_fs = fs_rx
        ratio = Fraction(fs_ref, fs_rx).limit_denominator(100000)
        rx = resample_poly(rx, ratio.numerator, ratio.denominator)
        fs_rx = fs_ref
        warning = f"RX remuestreado de {original_fs} Hz a {fs_ref} Hz para comparar."
    ref, rx, lag = align(ref, rx, fs_ref)
    n = min(len(ref), len(rx), max(1, int(max_seconds * fs_ref)))
    ref, rx = ref[:n], rx[:n]
    error = ref - rx
    mse = float(np.mean(error**2))
    ref_power = float(np.sum(ref**2))
    raw_snr = float(10 * np.log10(ref_power / max(float(np.sum(error**2)), 1e-30)))
    corr = float(np.corrcoef(ref, rx)[0, 1]) if np.std(ref) > 0 and np.std(rx) > 0 else float("nan")
    denominator = float(np.dot(rx, rx))
    gain = float(np.dot(ref, rx) / denominator) if denominator > 0 else 0.0
    fitted_error = ref - rx * gain
    fitted_snr = float(10 * np.log10(ref_power / max(float(np.sum(fitted_error**2)), 1e-30)))
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / received.stem
    view_n = min(n, max(10, int(0.04 * fs_ref)))
    time = np.arange(view_n) / fs_ref
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), constrained_layout=True)
    axes[0].plot(time * 1000, ref[:view_n], label="Referencia")
    axes[0].plot(time * 1000, rx[:view_n], label="Recibido", alpha=0.8)
    axes[0].set_title("Forma de onda alineada")
    axes[0].legend()
    axes[1].psd(ref, NFFT=min(8192, n), Fs=fs_ref, label="Referencia")
    axes[1].psd(rx, NFFT=min(8192, n), Fs=fs_ref, label="Recibido")
    axes[1].set_title("Espectro de referencia y recepción")
    axes[2].plot(time * 1000, (ref - rx)[:view_n])
    axes[2].set_title("Error temporal")
    axes[2].set_xlabel("Tiempo (ms)")
    fig.savefig(str(stem) + "_comparacion.png", dpi=160)
    plt.close(fig)
    report = {
        "reference": str(reference.resolve()),
        "received": str(received.resolve()),
        "reference_fs_hz": fs_ref,
        "received_fs_hz": rx_info.samplerate,
        "analyzed_duration_s": n / fs_ref,
        "alignment_lag_ms": lag / fs_ref * 1000,
        "mse": mse,
        "correlation": corr,
        "snr_raw_db": raw_snr,
        "snr_after_gain_fit_db": fitted_snr,
        "fitted_rx_to_ref_gain": gain,
        "experiment": metadata,
        "warnings": [warning] if warning else [],
    }
    Path(str(stem) + "_metricas.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"Comparado: {n / fs_ref:.3f} s | correlación {corr:.6f} | "
        f"MSE {mse:.6e} | SNR {raw_snr:.2f} dB"
    )
    if warning:
        print(f"  Aviso: {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepara, caracteriza y compara audio para el Lab 6 QPSK.",
        epilog=(
            "Ejemplo: python src/lab6_audio.py --entrada "
            "data/entrada/audio_original.wav --max-segundos 20"
        ),
    )
    parser.add_argument(
        "--entrada",
        default=str(DATA / "entrada" / "audio_original.wav"),
        help="Audio original; acepta cualquier frecuencia/canales (default: data/entrada/audio_original.wav).",
    )
    parser.add_argument(
        "--recibido",
        default=str(DATA / "resultados" / "audio_rx_capture.wav"),
        help="Captura RX a comparar (default: data/resultados/audio_rx_capture.wav).",
    )
    parser.add_argument(
        "--max-segundos",
        type=float,
        default=20.0,
        help="Máximo de audio comparado (default: 20 s).",
    )
    parser.add_argument(
        "--solo-preparar",
        action="store_true",
        help="Solo convierte y caracteriza; no compara una captura RX.",
    )
    parser.add_argument("--tx-power-db", type=float, help="Nivel TX de la captura.")
    parser.add_argument("--noise-amp", type=float, help="Amplitud lineal de ruido.")
    parser.add_argument("--rx-gain", type=float, help="Ganancia RX de la captura.")
    parser.add_argument("--scale", type=float, default=128.0, help="Escala Float/Char.")
    parser.add_argument("--sps", type=int, default=8, help="Muestras por símbolo.")
    parser.add_argument("--gnu-radio-version", help="Versión usada de GNU Radio.")
    parser.add_argument("--observacion", help="Nota sobre la captura o escucha.")
    args = parser.parse_args()
    source = Path(args.entrada).resolve()
    prepared = DATA / "entrada" / "audio_demo.wav"
    received = Path(args.recibido).resolve()
    if not source.is_file():
        parser.error(f"No existe el audio de entrada: {source}")
    if source == prepared.resolve():
        parser.error("La entrada debe ser el audio original, no audio_demo.wav.")
    target_fs = target_sample_rate()
    prepare_audio(source, prepared, target_fs)
    characterize(source, DATA / "evidencia" / "audio_original_analisis.png", target_fs)
    characterize(prepared, DATA / "evidencia" / "audio_demo_analisis.png", target_fs)
    if args.solo_preparar:
        return 0
    if not received.is_file():
        print(f"No existe captura RX; comparación omitida: {received}")
        return 0
    metadata = {
        "tx_power_db": args.tx_power_db,
        "noise_amp": args.noise_amp,
        "rx_gain": args.rx_gain,
        "scale": args.scale,
        "sps": args.sps,
        "gnu_radio_version": args.gnu_radio_version,
        "observation": args.observacion,
    }
    compare(prepared, received, DATA / "resultados", args.max_segundos, metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
