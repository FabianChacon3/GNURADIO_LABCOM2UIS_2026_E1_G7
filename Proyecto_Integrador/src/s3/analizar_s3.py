#!/usr/bin/env python3
"""Create analytical, reproducible figures for the S3 two-tap QPSK model.

These are calculations from the documented channel model. They are not GNU
Radio captures, RF measurements, PSD estimates, or BER results.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "figuras" / "s3"

RS = 32_000
SPS = 8
FS = RS * SPS
DELAY_SAMPLES = 8
SYMBOLS_PER_BIT = 2
QPSK = np.asarray([1 + 0j, 0 + 1j, -1 + 0j, 0 - 1j], dtype=np.complex128)

TESTS = (
    ("Referencia", 0.00 + 0.00j),
    ("Suave", 0.20 + 0.05j),
    ("Media", 0.35 + 0.15j),
    ("Fuerte", 0.50 + 0.20j),
)
COLORS = ("#59636e", "#2385c6", "#d58a00", "#b13b5b")
MODEL_LABEL = "Modelo analítico; sin AWGN ni medición GNU Radio"


def channel_taps(echo: complex) -> np.ndarray:
    taps = np.zeros(DELAY_SAMPLES + 1, dtype=np.complex128)
    taps[0] = 1.0 + 0.0j
    taps[DELAY_SAMPLES] = echo
    return taps


def frequency_response(echo: complex, frequencies_hz: np.ndarray) -> np.ndarray:
    return 1.0 + echo * np.exp(
        -2j * np.pi * frequencies_hz * DELAY_SAMPLES / FS
    )


def qpsk_indices_to_symbols(indices: np.ndarray) -> np.ndarray:
    return QPSK[np.asarray(indices, dtype=np.int64)]


def write_impulse_data() -> None:
    path = OUTPUT_DIR / "s3_respuesta_impulsional_modelo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["condicion", "muestra_n", "tap_real", "tap_imag", "origen"]
        )
        for name, echo in TESTS:
            for n, tap in enumerate(channel_taps(echo)):
                writer.writerow([name, n, tap.real, tap.imag, "modelo_analitico"])


def write_frequency_data(frequencies_hz: np.ndarray) -> None:
    path = OUTPUT_DIR / "s3_respuesta_frecuencial_modelo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "condicion",
                "frecuencia_hz",
                "magnitud_H",
                "ganancia_dB",
                "tap_eco_real",
                "tap_eco_imag",
                "origen",
            ]
        )
        for name, echo in TESTS:
            response = frequency_response(echo, frequencies_hz)
            gain_db = 20.0 * np.log10(np.maximum(np.abs(response), 1e-12))
            for freq, mag, db in zip(frequencies_hz, np.abs(response), gain_db):
                writer.writerow(
                    [
                        name,
                        freq,
                        mag,
                        db,
                        echo.real,
                        echo.imag,
                        "modelo_analitico",
                    ]
                )


def symbol_received(current: complex, previous: complex, echo: complex) -> complex:
    return current + echo * previous


def write_constellation_data() -> None:
    path = OUTPUT_DIR / "s3_constelaciones_modelo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "condicion",
                "simbolo_tx",
                "simbolo_previo",
                "tx_i",
                "tx_q",
                "rx_i",
                "rx_q",
                "tap_eco_real",
                "tap_eco_imag",
                "origen",
            ]
        )
        for name, echo in TESTS:
            for current_index, current in enumerate(QPSK):
                for previous_index, previous in enumerate(QPSK):
                    rx = symbol_received(current, previous, echo)
                    writer.writerow(
                        [
                            name,
                            current_index,
                            previous_index,
                            current.real,
                            current.imag,
                            rx.real,
                            rx.imag,
                            echo.real,
                            echo.imag,
                            "modelo_analitico_sin_ruido",
                        ]
                    )


def write_time_data(symbols: np.ndarray) -> None:
    previous = np.roll(symbols, 1)
    path = OUTPUT_DIR / "s3_secuencia_temporal_modelo.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "indice_simbolo",
                "tx_i",
                "tx_q",
                "condicion",
                "rx_i",
                "rx_q",
                "tap_eco_real",
                "tap_eco_imag",
                "origen",
            ]
        )
        for k, current in enumerate(symbols):
            for name, echo in TESTS:
                rx = symbol_received(current, previous[k], echo)
                writer.writerow(
                    [
                        k,
                        current.real,
                        current.imag,
                        name,
                        rx.real,
                        rx.imag,
                        echo.real,
                        echo.imag,
                        "modelo_analitico_sin_ruido",
                    ]
                )


def plot_impulse_response() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(9.0, 6.6), sharex=True)
    n = np.arange(DELAY_SAMPLES + 1)

    axes[0].stem(
        [0],
        [1],
        linefmt="#263746",
        markerfmt="o",
        basefmt=" ",
        label="Camino directo: h[0]=1",
    )
    for (name, echo), color in zip(TESTS, COLORS):
        axes[0].stem(
            [DELAY_SAMPLES],
            [echo.real],
            linefmt=color,
            markerfmt="o",
            basefmt=" ",
            label=f"{name}: {echo.real:.2f}",
        )
        axes[1].stem(
            [DELAY_SAMPLES],
            [echo.imag],
            linefmt=color,
            markerfmt="o",
            basefmt=" ",
            label=f"{name}: {echo.imag:.2f}",
        )
    for ax in axes:
        ax.set_xlim(-0.8, 9.0)
        ax.set_xticks(n)
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right", ncols=2, fontsize=8)
    axes[0].set_ylabel("Parte real de h[n]")
    axes[1].set_ylabel("Parte imaginaria de h[n]")
    axes[1].set_xlabel("Índice de muestra n")
    fig.suptitle(
        "Respuesta impulsional del canal S3\n"
        f"{MODEL_LABEL}; eco en n={DELAY_SAMPLES} (un símbolo)"
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "s3_respuesta_impulsional_modelo.png", dpi=220)
    plt.close(fig)


def plot_frequency_response(frequencies_hz: np.ndarray) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10.0, 7.2), sharex=True)
    for (name, echo), color in zip(TESTS, COLORS):
        response = frequency_response(echo, frequencies_hz)
        mag = np.abs(response)
        axes[0].plot(frequencies_hz / 1000.0, mag, color=color, label=name)
        axes[1].plot(
            frequencies_hz / 1000.0,
            20.0 * np.log10(np.maximum(mag, 1e-12)),
            color=color,
            label=name,
        )
    axes[0].set_ylabel("|H(f)|")
    axes[1].set_ylabel("20 log10 |H(f)| [dB]")
    axes[1].set_xlabel("Frecuencia f [kHz]")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend(title="Tap del eco")
    fig.suptitle(
        "Respuesta frecuencial del canal S3\n"
        f"{MODEL_LABEL}; no es una PSD"
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "s3_respuesta_frecuencial_modelo.png", dpi=220)
    plt.close(fig)


def plot_constellations() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 9.2), sharex=True, sharey=True)
    for ax, (name, echo), color in zip(axes.flat, TESTS, COLORS):
        received = np.asarray(
            [
                symbol_received(current, previous, echo)
                for current in QPSK
                for previous in QPSK
            ]
        )
        ax.scatter(
            QPSK.real,
            QPSK.imag,
            marker="x",
            s=70,
            linewidth=2,
            color="#172a3a",
            label="Tx QPSK",
        )
        ax.scatter(
            received.real,
            received.imag,
            s=38,
            color=color,
            alpha=0.85,
            label="Rx: todas las parejas actual/previo",
        )
        ax.set_title(f"{name}: eco {echo.real:.2f}{echo.imag:+.2f}j")
        ax.set_xlim(-1.9, 1.9)
        ax.set_ylim(-1.9, 1.9)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.25)
        ax.axhline(0, color="#788794", linewidth=0.7)
        ax.axvline(0, color="#788794", linewidth=0.7)
    axes[0, 0].set_ylabel("Q [amplitud normalizada]")
    axes[1, 0].set_ylabel("Q [amplitud normalizada]")
    axes[1, 0].set_xlabel("I [amplitud normalizada]")
    axes[1, 1].set_xlabel("I [amplitud normalizada]")
    axes[0, 0].legend(loc="upper left", fontsize=7)
    fig.suptitle(
        "Constelaciones QPSK en los instantes de símbolo\n"
        f"{MODEL_LABEL}; canal y[k]=x[k]+c·x[k−1]"
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "s3_constelaciones_modelo.png", dpi=220)
    plt.close(fig)


def plot_time_sequence(symbols: np.ndarray) -> None:
    previous = np.roll(symbols, 1)
    k = np.arange(len(symbols))
    fig, axes = plt.subplots(4, 1, figsize=(11.0, 9.5), sharex=True)
    for ax, (name, echo), color in zip(axes, TESTS, COLORS):
        received = symbols + echo * previous
        ax.step(k, symbols.real, where="mid", color="#34495e", linestyle="--", label="Tx I")
        ax.step(k, symbols.imag, where="mid", color="#8899a6", linestyle="--", label="Tx Q")
        ax.step(k, received.real, where="mid", color=color, label="Rx I")
        ax.step(
            k,
            received.imag,
            where="mid",
            color="#319b77",
            linestyle="-.",
            label="Rx Q",
        )
        ax.set_ylabel("Amplitud")
        ax.set_title(f"{name}: c={echo.real:.2f}{echo.imag:+.2f}j", loc="left", fontsize=10)
        ax.grid(True, alpha=0.22)
    axes[-1].set_xlabel("Índice de símbolo k")
    axes[0].legend(loc="upper right", ncols=4, fontsize=8)
    fig.suptitle(
        "Secuencia QPSK Tx y salida analítica del canal\n"
        f"{MODEL_LABEL}; símbolos aleatorios con semilla fija"
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "s3_secuencia_temporal_modelo.png", dpi=220)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frequencies_hz = np.linspace(-RS / 2.0, RS / 2.0, 801)
    rng = np.random.default_rng(20261112)
    indices = rng.integers(0, len(QPSK), size=32)
    symbols = qpsk_indices_to_symbols(indices)

    write_impulse_data()
    write_frequency_data(frequencies_hz)
    write_constellation_data()
    write_time_data(symbols)
    plot_impulse_response()
    plot_frequency_response(frequencies_hz)
    plot_constellations()
    plot_time_sequence(symbols)

    print(f"Analytical figures and CSV data written to: {OUTPUT_DIR}")
    print(f"Parameters: Rs={RS} sym/s, SPS={SPS}, fs={FS} samples/s, delay={DELAY_SAMPLES} samples")
    print("Source: deterministic two-tap model; no BER or PSD data are generated.")


if __name__ == "__main__":
    main()
