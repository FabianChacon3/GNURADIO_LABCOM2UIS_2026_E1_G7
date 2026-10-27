#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Laboratorio 6 - Tx/Rx de audio QPSK
# Description: Audio mono PCM16 a 44.1 kHz; control de nivel TX y ruido; visualización de audio y canal; captura WAV de recepción.
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class QPSK_TX_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Laboratorio 6 - Tx/Rx de audio QPSK", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Laboratorio 6 - Tx/Rx de audio QPSK")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_TX_RX")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.tabla_de_verdad_constelacion = tabla_de_verdad_constelacion = [0.77+0.77j, -0.77+0.77j, -0.77-0.77j, 0.77-0.77j]
        self.sample_rate_audio = sample_rate_audio = 44100
        self.Sps = Sps = 8
        self.tx_power_db = tx_power_db = 0
        self.samp_rate = samp_rate = sample_rate_audio*4*Sps
        self.noise_amp = noise_amp = 0.0
        self.h = h = [1]*Sps
        self.constelacion_qpsk = constelacion_qpsk = digital.constellation_calcdist(tabla_de_verdad_constelacion, [0, 1, 2, 3],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.constelacion_qpsk.set_npwr(1.0)

        ##################################################
        # Blocks
        ##################################################

        self._tx_power_db_range = qtgui.Range(-24, 6, 1, 0, 200)
        self._tx_power_db_win = qtgui.RangeWidget(self._tx_power_db_range, self.set_tx_power_db, "Nivel TX relativo (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_power_db_win)
        self._noise_amp_range = qtgui.Range(0.0, 0.20, 0.01, 0.0, 200)
        self._noise_amp_win = qtgui.RangeWidget(self._noise_amp_range, self.set_noise_amp, "Amplitud del ruido", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._noise_amp_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            "Señal compleja en el canal", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-2.5, 2.5)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_time_sink_audio = qtgui.time_sink_f(
            1024, #size
            sample_rate_audio, #samp_rate
            "Audio de entrada (forma de onda)", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_audio.set_update_time(0.10)
        self.qtgui_time_sink_audio.set_y_axis(-1.0, 1.0)

        self.qtgui_time_sink_audio.set_y_label('Amplitud', "")

        self.qtgui_time_sink_audio.enable_tags(True)
        self.qtgui_time_sink_audio.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_audio.enable_autoscale(False)
        self.qtgui_time_sink_audio.enable_grid(True)
        self.qtgui_time_sink_audio.enable_axis_labels(True)
        self.qtgui_time_sink_audio.enable_control_panel(False)
        self.qtgui_time_sink_audio.enable_stem_plot(False)


        labels = ['Audio mono', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_audio.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_audio.set_line_label(i, labels[i])
            self.qtgui_time_sink_audio.set_line_width(i, widths[i])
            self.qtgui_time_sink_audio.set_line_color(i, colors[i])
            self.qtgui_time_sink_audio.set_line_style(i, styles[i])
            self.qtgui_time_sink_audio.set_line_marker(i, markers[i])
            self.qtgui_time_sink_audio.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_audio_win = sip.wrapinstance(self.qtgui_time_sink_audio.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_audio_win)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro del canal QPSK", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_1.set_y_axis((-120), 5)
        self.qtgui_freq_sink_x_1.set_y_label('Magnitud relativa (dB)', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(True)
        self.qtgui_freq_sink_x_1.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_win)
        self.qtgui_freq_sink_audio = qtgui.freq_sink_f(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            sample_rate_audio, #bw
            "Espectro del audio de entrada", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_audio.set_update_time(0.20)
        self.qtgui_freq_sink_audio.set_y_axis((-100), 5)
        self.qtgui_freq_sink_audio.set_y_label('Magnitud relativa', 'dB')
        self.qtgui_freq_sink_audio.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_audio.enable_autoscale(False)
        self.qtgui_freq_sink_audio.enable_grid(True)
        self.qtgui_freq_sink_audio.set_fft_average(0.2)
        self.qtgui_freq_sink_audio.enable_axis_labels(True)
        self.qtgui_freq_sink_audio.enable_control_panel(False)
        self.qtgui_freq_sink_audio.set_fft_window_normalized(True)


        self.qtgui_freq_sink_audio.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_audio.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_audio.set_line_label(i, labels[i])
            self.qtgui_freq_sink_audio.set_line_width(i, widths[i])
            self.qtgui_freq_sink_audio.set_line_color(i, colors[i])
            self.qtgui_freq_sink_audio.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_audio_win = sip.wrapinstance(self.qtgui_freq_sink_audio.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_audio_win)
        self.qtgui_const_sink_x_1_0 = qtgui.const_sink_c(
            1024, #size
            "Constelación RX (símbolos muestreados)", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_1_0.set_update_time(0.10)
        self.qtgui_const_sink_x_1_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_1_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_1_0.enable_autoscale(False)
        self.qtgui_const_sink_x_1_0.enable_grid(True)
        self.qtgui_const_sink_x_1_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_1_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_1_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_1_0_win = sip.wrapinstance(self.qtgui_const_sink_x_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_1_0_win)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf(Sps, h)
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constelacion_qpsk)
        self.digital_chunks_to_symbols_xx_0_0 = digital.chunks_to_symbols_bc(tabla_de_verdad_constelacion, 1)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('data/entrada/audio_demo.wav', True)
        self.blocks_wavfile_sink_rx = blocks.wavfile_sink(
            'data/resultados/audio_rx_capture.wav',
            1,
            sample_rate_audio,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(2, gr.GR_MSB_FIRST)
        self.blocks_packed_to_unpacked_xx_0 = blocks.packed_to_unpacked_bb(2, gr.GR_MSB_FIRST)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(10**(tx_power_db / 20.0))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, Sps)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 128)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 128)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.audio_sink_0 = audio.sink(sample_rate_audio, '', True)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_freq_sink_x_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_wavfile_sink_rx, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.blocks_packed_to_unpacked_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_const_sink_x_1_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_packed_to_unpacked_xx_0, 0), (self.digital_chunks_to_symbols_xx_0_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.qtgui_freq_sink_audio, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.qtgui_time_sink_audio, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0_0, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.blocks_multiply_const_vxx_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "QPSK_TX_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tabla_de_verdad_constelacion(self):
        return self.tabla_de_verdad_constelacion

    def set_tabla_de_verdad_constelacion(self, tabla_de_verdad_constelacion):
        self.tabla_de_verdad_constelacion = tabla_de_verdad_constelacion
        self.digital_chunks_to_symbols_xx_0_0.set_symbol_table(self.tabla_de_verdad_constelacion)

    def get_sample_rate_audio(self):
        return self.sample_rate_audio

    def set_sample_rate_audio(self, sample_rate_audio):
        self.sample_rate_audio = sample_rate_audio
        self.set_samp_rate(self.sample_rate_audio*4*self.Sps)
        self.qtgui_freq_sink_audio.set_frequency_range(0, self.sample_rate_audio)
        self.qtgui_time_sink_audio.set_samp_rate(self.sample_rate_audio)

    def get_Sps(self):
        return self.Sps

    def set_Sps(self, Sps):
        self.Sps = Sps
        self.set_h([1]*self.Sps)
        self.set_samp_rate(self.sample_rate_audio*4*self.Sps)
        self.blocks_keep_one_in_n_0.set_n(self.Sps)

    def get_tx_power_db(self):
        return self.tx_power_db

    def set_tx_power_db(self, tx_power_db):
        self.tx_power_db = tx_power_db
        self.blocks_multiply_const_vxx_1.set_k(10**(self.tx_power_db / 20.0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_1.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.analog_noise_source_x_0.set_amplitude(self.noise_amp)

    def get_h(self):
        return self.h

    def set_h(self, h):
        self.h = h
        self.interp_fir_filter_xxx_0.set_taps(self.h)

    def get_constelacion_qpsk(self):
        return self.constelacion_qpsk

    def set_constelacion_qpsk(self, constelacion_qpsk):
        self.constelacion_qpsk = constelacion_qpsk
        self.digital_constellation_decoder_cb_0.set_constellation(self.constelacion_qpsk)




def main(top_block_cls=QPSK_TX_RX, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
