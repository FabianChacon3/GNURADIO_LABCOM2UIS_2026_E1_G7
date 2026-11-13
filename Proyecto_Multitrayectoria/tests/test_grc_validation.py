"""Reproducible checks against the GNU Radio blocks embedded in the project GRCs."""

from __future__ import annotations

import math
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from gnuradio import blocks, channels, digital, filter, gr


PROJECT = Path(__file__).resolve().parents[1]
GRC = PROJECT / "grc"
S3_FILES = {
    "QPSK": GRC / "archivos_modificados/S3/QPSK/Enlace_S3_QPSK_Multitrayectoria_Grupo3.grc",
    "BPSK": GRC / "archivos_modificados/S3/BPSK/Enlace_S3_BPSK_Multitrayectoria_Grupo3.grc",
}
TX_FILE = GRC / "archivos_modificados/SDR_Imagen/LAB_TX_16QAM_HackRF_IMAGEN.grc"
RX_FILE = GRC / "archivos_modificados/SDR_Imagen/LAB_RX_16QAM_HackRF_IMAGEN.grc"
ECHO_CASES = ((0.0, 0.0), (0.20, 0.05), (0.35, 0.15), (0.50, 0.20))


def load_grc(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def block_named(doc: dict, name: str) -> dict:
    return next(block for block in doc["blocks"] if block["name"] == name)


def variable(doc: dict, name: str, overrides: dict | None = None):
    overrides = overrides or {}
    pending = {
        block["name"]: block["parameters"]["value"]
        for block in doc["blocks"]
        if block["id"].startswith("variable")
        and "value" in block.get("parameters", {})
        and block["name"] not in overrides
    }
    scope = {"math": math, "np": np, "complex": complex, "len": len}
    scope.update(overrides)
    while pending:
        progressed = False
        for key, expression in list(pending.items()):
            try:
                scope[key] = eval(expression, scope, {})
            except (NameError, SyntaxError, TypeError, ValueError):
                continue
            del pending[key]
            progressed = True
        if not progressed:
            break
    if name not in scope:
        raise ValueError(f"No se pudo evaluar la variable GRC {name!r}")
    return scope[name]  # Expressions are read from this project's GRC.


def embedded_block(path: Path, name: str, module_path: Path | None = None) -> dict:
    block = block_named(load_grc(path), name)
    namespace = {
        "__name__": f"test_{name}",
        "__file__": str(module_path or path.with_suffix(".py")),
    }
    source = block["parameters"]["_source_code"]
    exec(compile(source, str(path), "exec"), namespace)
    return namespace


def run_top_block(source, middle, sink):
    top = gr.top_block()
    top.connect(source, middle, sink)
    top.run()
    return np.asarray(sink.data())


class S3Validation(unittest.TestCase):
    def test_known_bits_through_gnuradio_blocks(self):
        bits = [0, 0, 0, 1, 1, 0, 1, 1]
        for modulation, grc_path, bps, expected in (
            ("QPSK", S3_FILES["QPSK"], 2, [1 + 0j, 1j, -1 + 0j, -1j]),
            ("BPSK", S3_FILES["BPSK"], 1,
             [-1 + 0j, -1 + 0j, -1 + 0j, 1 + 0j,
              1 + 0j, -1 + 0j, 1 + 0j, 1 + 0j]),
        ):
            with self.subTest(modulation=modulation):
                doc = load_grc(grc_path)
                self.assertEqual(int(block_named(doc, "blocks_pack_k_bits_bb_0")["parameters"]["k"]), 8)
                unpack = block_named(doc, "blocks_packed_to_unpacked_xx_0")["parameters"]
                self.assertEqual(unpack["bits_per_chunk"], "bps")
                self.assertEqual(unpack["endianness"], "gr.GR_MSB_FIRST")
                self.assertEqual(variable(doc, "bps"), bps)
                self.assertEqual(variable(doc, "Rs"), 32000)
                self.assertEqual(variable(doc, "samp_rate"), 256000)
                self.assertEqual(variable(doc, "Rb"), 32000 * bps)
                self.assertEqual(list(variable(doc, "tabla_de_verdad_constelacion")), expected[:4] if bps == 2 else [-1 + 0j, 1 + 0j])

                source = blocks.vector_source_b(bits, False)
                pack = blocks.pack_k_bits_bb(8)
                unpack_bits = blocks.packed_to_unpacked_bb(bps, gr.GR_MSB_FIRST)
                mapper = digital.chunks_to_symbols_bc(
                    list(variable(doc, "tabla_de_verdad_constelacion")), 1)
                sink = blocks.vector_sink_c()
                top = gr.top_block()
                top.connect(source, pack, unpack_bits, mapper, sink)
                top.run()
                np.testing.assert_allclose(np.asarray(sink.data()), expected, atol=1e-7)

    def test_channel_taps_and_actual_channel_model(self):
        impulse = np.zeros(64, dtype=np.complex64)
        impulse[16] = 1
        for real, imag in ECHO_CASES:
            with self.subTest(echo=(real, imag)):
                coefficient = complex(real, imag)
                taps = [1 + 0j] + [0j] * 7 + [coefficient]

                # The independent FIR reference has h[0]=1 and h[8]=c exactly.
                fir = filter.fir_filter_ccc(1, taps)
                fir_out = run_top_block(
                    blocks.vector_source_c(impulse.tolist(), False),
                    fir,
                    blocks.vector_sink_c(),
                )
                np.testing.assert_allclose(fir_out[16:25], taps, atol=1e-7)

                # GNU Radio channel_model adds a fixed three-sample MMSE startup delay.
                # Check tap spacing and coefficients relative to its direct path.
                channel = channels.channel_model(0.0, 0.0, 1.0, taps, 0, False)
                sink = blocks.vector_sink_c()
                channel_out = run_top_block(
                    blocks.vector_source_c(impulse.tolist(), False), channel, sink)
                active = np.flatnonzero(np.abs(channel_out) > 1e-4)
                expected_active = [13] if coefficient == 0 else [13, 21]
                self.assertEqual(active.tolist(), expected_active)
                self.assertAlmostEqual(channel_out[13].real, 1.0, places=6)
                self.assertAlmostEqual(channel_out[13].imag, 0.0, places=6)
                if coefficient != 0:
                    self.assertAlmostEqual(channel_out[21].real, real, places=6)
                    self.assertAlmostEqual(channel_out[21].imag, imag, places=6)

    def test_grc_channel_taps_and_viewer_connections(self):
        for modulation, path in S3_FILES.items():
            with self.subTest(modulation=modulation):
                doc = load_grc(path)
                self.assertEqual(variable(doc, "Sps"), 8)
                self.assertEqual(variable(doc, "samp_rate"), 256000)
                self.assertAlmostEqual(float(variable(doc, "noise_amp")), 0.05)
                self.assertEqual(len(variable(doc, "taps_canal")), 9)
                self.assertEqual(variable(doc, "taps_canal")[0], 1 + 0j)
                self.assertEqual(variable(doc, "taps_canal")[-1], 0.35 + 0.15j)
                channel_name = "channels_channel_model_0"
                viewer_names = {
                    block["name"] for block in doc["blocks"]
                    if block["id"] in {
                        "qtgui_const_sink_x", "qtgui_freq_sink_x", "qtgui_time_sink_x"
                    }
                }
                connected = {
                    connection[2] for connection in doc["connections"]
                    if connection[0] == channel_name and connection[2] in viewer_names
                }
                self.assertEqual(connected, viewer_names)


class ImageProtocolValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="grc-image-test-")
        self.temp_path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def _tx_rx(self):
        tx_module = embedded_block(TX_FILE, "tx_imagen", TX_FILE.with_suffix(".py"))
        rx_module = embedded_block(RX_FILE, "rx_imagen", RX_FILE.with_suffix(".py"))
        return tx_module, rx_module

    def test_tables_header_preamble_and_all_phase_maps(self):
        tx_module, rx_module = self._tx_rx()
        tx_doc, rx_doc = load_grc(TX_FILE), load_grc(RX_FILE)
        tx_points = np.asarray(variable(tx_doc, "tabla_de_verdad_constelacion"), np.complex64)
        rx_points = np.asarray(rx_module["POINTS"], np.complex64)
        np.testing.assert_allclose(tx_points, rx_points, atol=1e-7)
        self.assertEqual(tx_module["HDR_FMT"], rx_module["HDR_FMT"])
        self.assertEqual(struct.calcsize(tx_module["HDR_FMT"]), 12)
        self.assertEqual(tx_module["PRE_LEN"], rx_module["PRE_LEN"])
        self.assertEqual(tx_module["GUARD_LEN"], rx_module["GUARD_LEN"])
        np.testing.assert_array_equal(tx_module["PREAMBLE"], rx_module["PREAMBLE"])
        np.testing.assert_array_equal(
            tx_module["prng"](777123, 20, 8), rx_module["prng"](777123, 20, 8))

        rx = rx_module["blk"](out_path=str(self.temp_path / "unused.png"))
        for rotation in range(4):
            with self.subTest(rotation=rotation * 90):
                rotated = rx_points * (1j ** rotation)
                decisions = np.argmin(
                    np.abs(rotated[:, None] - rx_points[None, :]) ** 2, axis=1)
                recovered = rx.rotation_maps[rotation][decisions]
                np.testing.assert_array_equal(recovered, np.arange(16))

    def test_constellation_receiver_outputs_aligned_indices_and_samples(self):
        doc = load_grc(RX_FILE)
        points = np.asarray(variable(doc, "tabla_de_verdad_constelacion"), np.complex64)
        constellation = digital.constellation_calcdist(
            points.tolist(), list(range(16)), 4,
            digital.constellation.POWER_NORMALIZATION).base()
        receiver = digital.constellation_receiver_cb(
            constellation, 2 * math.pi / 100, -0.25, 0.25)
        indices = np.tile(np.arange(16, dtype=np.uint8), 20)
        samples = points[indices]
        source = blocks.vector_source_c(samples.tolist(), False)
        index_sink = blocks.vector_sink_b()
        sample_sink = blocks.vector_sink_c()
        nulls = [blocks.null_sink(gr.sizeof_float) for _ in range(3)]
        top = gr.top_block()
        top.connect(source, receiver)
        top.connect((receiver, 0), index_sink)
        for port, sink in enumerate(nulls, start=1):
            top.connect((receiver, port), sink)
        top.connect((receiver, 4), sample_sink)
        top.run()
        decisions = np.asarray(index_sink.data())
        synchronized = np.asarray(sample_sink.data())
        self.assertEqual(len(decisions), len(synchronized))
        np.testing.assert_array_equal(decisions, indices)
        np.testing.assert_allclose(synchronized, samples, atol=1e-6)

    def _make_test_image(self, path: Path):
        data = np.arange(7 * 5 * 3, dtype=np.uint8).reshape((5, 7, 3))
        Image.fromarray(data, "RGB").save(path)
        return data

    def test_missing_image_fails_and_synthetic_image_requires_test_mode(self):
        tx_module, _ = self._tx_rx()
        missing = self.temp_path / "absent.png"
        with self.assertRaisesRegex(FileNotFoundError, "No se encontro el PNG"):
            tx_module["load_image"](str(missing), 7, 5, 3, False)
        generated = tx_module["load_image"](str(missing), 7, 5, 3, True)
        self.assertEqual(generated.size, (7, 5))

        relative = tx_module["resolve_image_path"](
            "../../../figures/escenario/Logouis.png")
        self.assertTrue(Path(relative).is_file())

    def test_optional_logs_are_anchored_to_the_generated_flowgraph(self):
        doc = load_grc(RX_FILE)
        block = block_named(doc, "rx_log_iq_64ksps")
        self.assertEqual(block["id"], "epy_block")
        self.assertEqual(block["states"]["state"], "disabled")
        module_path = self.temp_path / "flowgraph" / "generated.py"
        module_path.parent.mkdir()
        namespace = {
            "__name__": "test_optional_log",
            "__file__": str(module_path),
        }
        exec(compile(block["parameters"]["_source_code"], str(RX_FILE), "exec"), namespace)
        logger = namespace["blk"](
            file_path="data/resultados/RX_IQ_64ksps.c64", item_type="complex")
        samples = np.asarray([1 + 2j, 3 + 4j], np.complex64)
        self.assertEqual(logger.work([samples], []), len(samples))
        logger.stop()
        log_path = module_path.parent / "data/resultados/RX_IQ_64ksps.c64"
        self.assertEqual(log_path.read_bytes(), samples.tobytes())

    def test_end_to_end_image_crc_pixels_and_four_rotations(self):
        tx_module, rx_module = self._tx_rx()
        input_path = self.temp_path / "small.png"
        expected_pixels = self._make_test_image(input_path)
        points = np.asarray(
            variable(load_grc(TX_FILE), "tabla_de_verdad_constelacion"), np.complex64)
        for rotation in range(4):
            with self.subTest(rotation=rotation * 90):
                phase_dir = self.temp_path / f"phase-{rotation}"
                phase_dir.mkdir()
                rx_module["__file__"] = str(phase_dir / "generated.py")
                tx = tx_module["blk"](
                    image_path=str(input_path), width=7, height=5,
                    channels=3, payload_len=31, test_mode=False)
                tx._prepare_frames()
                indices = tx.frame_all.copy()
                samples = points[indices] * (1j ** rotation)
                decisions = np.argmin(
                    np.abs(samples[:, None] - points[None, :]) ** 2, axis=1
                ).astype(np.uint8)
                rx = rx_module["blk"](
                    out_path="data/resultados/rx_imagen.png",
                    payload_len=31, save_every=1)
                n = len(indices)
                outputs = [np.empty(n, np.float32) for _ in range(3)]
                self.assertEqual(rx.work([decisions, samples], outputs), n)
                self.assertEqual(rx.progress, 100.0)
                self.assertEqual(rx.ok_pct, 100.0)
                self.assertLess(rx.evm, 1e-4)
                output_path = phase_dir / "data/resultados/rx_imagen.png"
                self.assertTrue(output_path.is_file())
                with Image.open(output_path) as reconstructed:
                    self.assertEqual(reconstructed.size, (7, 5))
                    self.assertEqual(reconstructed.mode, "RGB")
                    np.testing.assert_array_equal(
                        np.asarray(reconstructed), expected_pixels)

    def test_corrupt_frame_crc_is_rejected(self):
        tx_module, rx_module = self._tx_rx()
        input_path = self.temp_path / "crc.png"
        self._make_test_image(input_path)
        tx = tx_module["blk"](
            image_path=str(input_path), width=7, height=5,
            channels=3, payload_len=31, test_mode=False)
        tx._prepare_frames()
        frame_len = (tx_module["PRE_LEN"] +
                     2 * (tx_module["HDR_LEN"] + 31 + 4) +
                     tx_module["GUARD_LEN"])
        damaged = tx.frame_all[:frame_len].copy()
        damaged[tx_module["PRE_LEN"] + 8] ^= 1
        points = np.asarray(
            variable(load_grc(TX_FILE), "tabla_de_verdad_constelacion"), np.complex64)
        samples = points[damaged]
        rx = rx_module["blk"](out_path=str(self.temp_path / "bad.png"), payload_len=31)
        outputs = [np.empty(len(damaged), np.float32) for _ in range(3)]
        rx.work([damaged, samples], outputs)
        self.assertEqual(rx.total_frames, 1)
        self.assertEqual(rx.crc_ok_frames, 0)
        self.assertEqual(rx.progress, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
