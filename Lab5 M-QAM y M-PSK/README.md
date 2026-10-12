# 📡 Laboratorio 5: Modulación M-QAM y M-PSK en GNU Radio

# Laboratorio 5: Modulación M-QAM y M-PSK en GNU Radio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/FabianChacon3/GNURADIO_LABCOM2UIS_2026_E1_G7/blob/main/LICENSE)

**Asignatura:** Comunicaciones II (27145)  
**Escuela:** Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T)  
**Institución:** Universidad Industrial de Santander (UIS)  

---

## Descripción del Proyecto

Este repositorio contiene la implementación, simulación y análisis de esquemas de modulación digital pasobanda M-PSK ($M \in \{2, 4, 8\}$) y M-QAM ($M \in \{4, 16, 64\}$) utilizando **GNU Radio Companion (GRC)**.

El objetivo principal es evaluar el impacto del orden de modulación ($M$), el número de muestras por símbolo ($Sps$) y los niveles de ruido blanco gaussiano aditivo (AWGN) sobre:

- La distribución espacial en el plano de constelación ($I/Q$).
- La tasa de transmisión de datos ($R_b = R_s \cdot \log_2 M$).
- El ancho de banda ocupado y la densidad espectral de potencia.
- La magnitud del vector de error (EVM) y la relación señal a ruido (SNR).

---

## Resumen Ejecutivo y Hallazgos Clave

- **Eficiencia Espectral vs. Robustez al Ruido:** A medida que se incrementa el orden de modulación ($M = 2 \to 64$), la tasa de transmisión $R_b$ aumenta logarítmicamente. Sin embargo, la menor separación euclidiana entre símbolos adyacentes reduce el margen contra el ruido gaussiano (AWGN).
- **Comportamiento del EVM y SNR:**
  - **4-QAM (QPSK):** Mantiene alta tolerancia al ruido; conserva la separabilidad de cuadrantes incluso con amplitudes de ruido elevadas.
  - **64-QAM:** Requiere niveles de SNR superiores a 25 dB ($\text{EVM} < 8\%$). Amplitudes de ruido elevadas generan solapamiento entre símbolos, degradando la tasa de error de bit (BER).
- **Efecto de las Muestras por Símbolo ($Sps$):** Modifica la representación discreta y la resolución espectral en el tiempo/frecuencia sin alterar la tasa de bits efectiva ($R_b$).
---

## 📁 Estructura del Repositorio

```text
.
├── 📄 LICENSE              # Licencia MIT del repositorio
├── 📄 README.md            # Documentación general del laboratorio
├── 📂 data/                # Evidencias experimentales y capturas
│   └── 📂 imagenes/
│       ├── 📂 PART1/       # Capturas de tiempo, frecuencia y constelación (Parte 1)
│       └── 📂 PART2/       # Diagramas de constelación para análisis EVM / SNR (Parte 2)
├── 📂 docs/                # Informe de laboratorio en formato PDF
│   └── 📄 Informe_Lab5_Comunicaciones_II.pdf
└── 📂 src/                 # Código fuente y flujogramas de GNU Radio
    ├── 📄 lab5_mqam_mpsk.grc # Diagrama de flujo principal de GRC
    └── 📄 top_block.py       # Script de Python generado por GRC
```
