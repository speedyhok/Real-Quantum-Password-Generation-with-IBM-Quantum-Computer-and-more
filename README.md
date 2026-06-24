# 🔑 Real Quantum Password Generation with IBM Quantum Computer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.4.2-purple.svg)](https://qiskit.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An advanced **Quantum Random Number Generator (QRNG)** application that leverages the intrinsic non-deterministic behavior of quantum superposition to generate cryptographically secure passwords. 

This project implements a web-based dashboard and a CLI interface to generate passwords using both **physical superconducting quantum hardware** (via IBM Quantum Services) and **local quantum simulations** (via Qiskit Aer). It then performs a rigorous statistical comparison against classical random number generators (PRNG and CSPRNG) using NIST randomness tests.

---

## 👨‍💻 Author Information

* **Author:** Mohibul Hoque
* **Email:** [Hokworks@gmail.com](mailto:Hokworks@gmail.com)
* **LinkedIn:** [linkedin.com/in/speedymohibul](https://www.linkedin.com/in/speedymohibul)
* **GitHub Repository:** [Real-Quantum-Password-Generation-with-IBM-Quantum-Computer-and-more](https://github.com/speedyhok/Real-Quantum-Password-Generation-with-IBM-Quantum-Computer-and-more)

---

## 🌟 Key Features

1. **True Physical Randomness**: Maps raw bits from Qiskit quantum circuits utilizing Hadamard gates ($H$) and computational basis measurements.
2. **Modulo Bias Mitigation**: Implements **Rejection Sampling** when mapping random bits to password alphabets to guarantee absolute uniformity.
3. **NIST Statistical Test Suite**: Analyzes random bitstreams using:
   - **Shannon Entropy** (Ideal target: 1.0)
   - **NIST Monobit Frequency Test** (Proportion of 0s vs 1s)
   - **NIST Runs Test** (Transition frequency between bits)
   - **Chi-Square Goodness-of-Fit Tests** (Bit-pair uniformity)
   - **Serial Correlation (Lag 1)** (Adjacent bit dependency)
4. **Password Strength Evaluation**: Integrates the `zxcvbn` library to evaluate theoretical entropy and calculate estimated offline/online cracking times.
5. **Interactive UI & CLI**: Beautiful dark-themed Streamlit application with glassmorphism UI cards, real-time plotting, and a fully interactive Command Line Interface.

---

## 🛠️ Installation & Setup

Ensure you have Python 3.10+ installed.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/speedyhok/Real-Quantum-Password-Generation-with-IBM-Quantum-Computer-and-more.git
   cd Real-Quantum-Password-Generation-with-IBM-Quantum-Computer-and-more
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run

### 1. Launch the Streamlit Web Application
Run the web dashboard locally:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

### 2. Run the Interactive CLI
Run the terminal-based password generator:
```bash
python cli.py
```

---

## 📐 The Physics & Mathematics

### Quantum Superposition
A classical bit can only be `0` or `1`. A qubit is initialized in the state $|0\rangle$, and applying a Hadamard ($H$) gate places it into an equal superposition:
$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$$

Upon measurement, the wave function collapses to $|0\rangle$ or $|1\rangle$ with exactly $50\%$ probability, yielding true, non-deterministic physical entropy.

### Modulo Bias & Rejection Sampling
Using basic modulo arithmetic (e.g. `index = random_int % alphabet_size`) creates bias if the range of the random number is not a perfect multiple of the alphabet size.

To resolve this, this project determines the minimum bit length $k$ to represent the alphabet, calculates the maximum uniform multiple range, and rejects any values falling outside this boundary, requesting fresh quantum bits if rejected.

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
