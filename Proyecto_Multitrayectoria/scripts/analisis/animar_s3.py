#!/usr/bin/env python3
"""Create a labeled analytical animation of the S3 QPSK channel.

The outputs illustrate the documented two-tap model. They are not GNU Radio
captures, RF measurements, PSD estimates, or BER/EVM measurements.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from analizar_s3 import QPSK, TESTS, MODEL_LABEL, previous_symbols


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "images" / "figuras_s3"
BLOG_MEDIA_DIR = PROJECT_ROOT / "blog" / "media"
SEED = 20261112
SYMBOL_COUNT = 32
NOISE_STD = 0.05


def build_figure(symbols: np.ndarray, noise_std: float = 0.0):
    previous = previous_symbols(symbols)
    noise_rng = np.random.default_rng(SEED + 1)
    noise_by_frame = (
        noise_rng.normal(0.0, noise_std / np.sqrt(2), (len(TESTS), SYMBOL_COUNT))
        + 1j * noise_rng.normal(0.0, noise_std / np.sqrt(2), (len(TESTS), SYMBOL_COUNT))
        if noise_std
        else np.zeros((len(TESTS), SYMBOL_COUNT), dtype=np.complex128)
    )
    figure, axes = plt.subplots(2, 2, figsize=(12.8, 8.0))
    figure.patch.set_facecolor("#f7fafc")
    figure.suptitle(
        "Canal S3: cómo cambia la salida QPSK al aumentar el eco\n"
        + ("Modelo analítico con AWGN; no es una captura de GNU Radio"
           if noise_std else
           "Modelo analítico sin AWGN; no es una captura de GNU Radio"),
        fontsize=16,
        fontweight="bold",
    )
    constellation_ax, time_ax, impulse_ax, text_ax = axes.flat

    for ax in (constellation_ax, time_ax, impulse_ax, text_ax):
        ax.set_facecolor("#ffffff")
        ax.grid(True, alpha=0.22)

    constellation_ax.scatter(
        QPSK.real,
        QPSK.imag,
        marker="x",
        s=100,
        linewidth=2,
        color="#172a3a",
        label="Tx ideal",
    )
    constellation_ax.set_title("Muestras en los instantes de símbolo")
    constellation_ax.set_xlabel("I")
    constellation_ax.set_ylabel("Q")
    constellation_ax.set_aspect("equal", adjustable="box")
    constellation_ax.set_xlim(-2.0, 2.0)
    constellation_ax.set_ylim(-2.0, 2.0)
    constellation_ax.legend(loc="upper left")

    time_ax.set_title("Secuencia determinista: Tx frente a salida del canal")
    time_ax.set_xlabel("Índice de símbolo k")
    time_ax.set_ylabel("Amplitud")
    time_ax.set_xlim(0, SYMBOL_COUNT - 1)
    time_ax.set_ylim(-2.1, 2.1)
    time_ax.plot(
        np.arange(SYMBOL_COUNT),
        symbols.real,
        "--",
        color="#34495e",
        alpha=0.7,
        label="Tx I",
    )
    time_ax.plot(
        np.arange(SYMBOL_COUNT),
        symbols.imag,
        "--",
        color="#8899a6",
        alpha=0.7,
        label="Tx Q",
    )

    impulse_ax.set_title("Respuesta impulsional h[n]")
    impulse_ax.set_xlabel("Muestra n")
    impulse_ax.set_ylabel("Coeficiente")
    impulse_ax.set_xlim(-0.5, 8.5)
    impulse_ax.set_ylim(-0.1, 0.65)
    impulse_ax.set_xticks(range(9))
    impulse_ax.stem([0], [1], linefmt="#172a3a", markerfmt="o", basefmt=" ")

    text_ax.axis("off")
    text_ax.text(
        0.02,
        0.96,
        "Lectura del experimento",
        transform=text_ax.transAxes,
        fontsize=13,
        fontweight="bold",
        va="top",
    )

    def update(frame: int):
        name, echo = TESTS[frame]
        color = ("#59636e", "#2385c6", "#d58a00", "#b13b5b")[frame]
        received = symbols + echo * previous + noise_by_frame[frame]

        for collection in list(constellation_ax.collections[1:]):
            collection.remove()
        constellation_ax.scatter(
            received.real,
            received.imag,
            s=38,
            color=color,
            alpha=0.82,
            label=f"Rx: {name}",
        )
        constellation_ax.legend(loc="upper left")
        constellation_ax.set_title(
            f"Constelación de salida: {name}  |  c={echo.real:.2f}{echo.imag:+.2f}j"
        )

        for line in list(time_ax.lines[2:]):
            line.remove()
        time_ax.plot(
            np.arange(SYMBOL_COUNT),
            received.real,
            color=color,
            linewidth=1.8,
            label="Rx I",
        )
        time_ax.plot(
            np.arange(SYMBOL_COUNT),
            received.imag,
            color="#319b77",
            linestyle="-.",
            linewidth=1.8,
            label="Rx Q",
        )
        time_ax.legend(loc="upper right", ncols=4, fontsize=8)

        for artist in list(impulse_ax.collections):
            artist.remove()
        for artist in list(impulse_ax.lines):
            artist.remove()
        impulse_ax.stem([0], [1], linefmt="#172a3a", markerfmt="o", basefmt=" ")
        impulse_ax.stem(
            [8],
            [echo.real],
            linefmt=color,
            markerfmt="o",
            basefmt=" ",
            label=f"Re(c)={echo.real:.2f}",
        )
        impulse_ax.stem(
            [8],
            [echo.imag],
            linefmt="#319b77",
            markerfmt="s",
            basefmt=" ",
            label=f"Im(c)={echo.imag:.2f}",
        )
        impulse_ax.set_title(f"Respuesta impulsional: camino directo + eco en n=8")
        impulse_ax.legend(loc="upper right", fontsize=8)

        magnitude = abs(echo)
        phase = np.degrees(np.angle(echo)) if magnitude else 0.0
        for artist in list(text_ax.texts):
            artist.remove()
        text_ax.text(
            0.02,
            0.96,
            (
                f"Condición: {name}\n\n"
                f"Tap directo: h[0] = 1+0j\n"
                f"Tap eco: h[8] = {echo.real:.2f}{echo.imag:+.2f}j\n"
                f"|c| = {magnitude:.3f}\n"
                f"Fase del eco = {phase:.1f}°\n\n"
                "y[k] = x[k] + c·x[k−1]\n"
                "El eco mezcla el símbolo anterior y\n"
                "puede desplazar la constelación.\n\n"
            )
            + (
                f"Ruido complejo AWGN: sigma={noise_std:.2f}\n\n"
                if noise_std
                else ""
            )
            + (
                "Modelo analítico determinista; sin medición GNU Radio"
                if not noise_std
                else "Modelo analítico reproducible; AWGN sintético"
            ),
            transform=text_ax.transAxes,
            fontsize=12,
            va="top",
            linespacing=1.35,
        )
        return []

    return figure, update


def write_summary_table() -> Path:
    path = PROJECT_ROOT / "data" / "figuras_s3" / "s3_tabla_resumen.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "condicion",
                "eco_real",
                "eco_imag",
                "magnitud_eco",
                "fase_grados",
                "potencia_media_relativa",
                "retardo_muestras",
                "retardo_us",
                "ruido_declarado",
                "interpretacion",
            ]
        )
        interpretations = (
            "Sin eco; salida ideal",
            "ISI leve; desplazamiento pequeño",
            "ISI moderada; mayor dispersion",
            "ISI fuerte; desplazamiento dominante",
        )
        for (name, echo), interpretation in zip(TESTS, interpretations):
            writer.writerow(
                [
                    name,
                    echo.real,
                    echo.imag,
                    abs(echo),
                    np.degrees(np.angle(echo)) if echo else "",
                    1 + abs(echo) ** 2,
                    8,
                    31.25,
                    NOISE_STD,
                    interpretation,
                ]
            )
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BLOG_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    symbols = QPSK[rng.integers(0, len(QPSK), size=SYMBOL_COUNT)]
    print(f"Summary table: {write_summary_table()}")
    for suffix, noise_std in (("", 0.0), ("_ruido", NOISE_STD)):
        figure, update = build_figure(symbols, noise_std)
        png_path = OUTPUT_DIR / f"s3_cambios_parametros_modelo{suffix}.png"
        gif_path = OUTPUT_DIR / f"s3_cambios_parametros_modelo{suffix}.gif"
        blog_gif_path = BLOG_MEDIA_DIR / gif_path.name
        update(0)
        figure.savefig(png_path, dpi=180, bbox_inches="tight")
        animation = FuncAnimation(
            figure,
            update,
            frames=len(TESTS),
            interval=1600,
            repeat=True,
            blit=False,
        )
        animation.save(gif_path, writer=PillowWriter(fps=0.7), dpi=120)
        animation.save(blog_gif_path, writer=PillowWriter(fps=0.7), dpi=120)
        plt.close(figure)
        print(f"Static figure: {png_path}")
        print(f"GIF for report: {gif_path}")
        print(f"GIF for blog: {blog_gif_path}")


if __name__ == "__main__":
    main()
