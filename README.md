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

## 📊 Statistical Randomness Analysis Methods

To rigorously verify the quality of the generated random numbers, the project implements five distinct statistical testing methods in `randomness_tests.py` using NumPy and SciPy:

### 1. Shannon Entropy
Shannon entropy measures the average information density and unpredictability per bit in the sequence.
* **Formula**:
  $$H = -\sum_{i \in \{0, 1\}} p_i \log_2(p_i) = - \left( p_0 \log_2(p_0) + p_1 \log_2(p_1) \right)$$
  where:
  - $p_0$ is the proportion of `0`s in the bitstring ($N_0 / N$).
  - $p_1$ is the proportion of `1`s in the bitstring ($N_1 / N$).
* **Interpretation**: The maximum possible entropy for a binary source is $1.0$ bits per bit, which occurs when $p_0 = p_1 = 0.5$. Any bias (e.g., more `0`s than `1`s) reduces this value.

### 2. NIST SP 800-22 Frequency (Monobit) Test
This test determines whether the proportion of ones and zeros is approximately equal, as expected from a truly random uniform distribution.
* **Calculation Steps**:
  1. Convert the binary digits $X_i \in \{0, 1\}$ to normalized values $S_i \in \{-1, +1\}$:
     $$S_i = 2X_i - 1$$
  2. Compute the sum of the sequence: $S_n = \sum_{i=1}^n S_i$.
  3. Calculate the test statistic:
     $$S_{obs} = \frac{|S_n|}{\sqrt{n}}$$
  4. Compute the p-value using the complementary error function (`erfc`):
     $$P\text{-value} = \text{erfc}\left( \frac{S_{obs}}{\sqrt{2}} \right)$$
* **Interpretation**: A $P\text{-value} \ge 0.01$ indicates that the sequence passes. A very low p-value suggests that the stream has a statistically significant imbalance of `0`s or `1`s.

### 3. NIST SP 800-22 Runs Test
A "run" is an uninterrupted sequence of identical bits (e.g., `1111` or `000`). This test determines whether the frequency of transitions between `0` and `1` is normal.
* **Calculation Steps**:
  1. Let $\pi = \frac{1}{n}\sum_{i=1}^n X_i$ be the proportion of ones in the stream.
  2. Perform a pre-test check: if $|\pi - 0.5| \ge \tau$ where $\tau = 2/\sqrt{n}$, the runs test fails immediately ($P\text{-value} = 0.0$).
  3. Count the total observed runs $V_n$:
     $$V_n = 1 + \sum_{j=1}^{n-1} (X_j \oplus X_{j+1})$$
     where $\oplus$ represents the XOR operator (which yields `1` if a transition occurs).
  4. Compute the p-value:
     $$P\text{-value} = \text{erfc}\left( \frac{|V_n - 2n\pi(1-\pi)|}{2\sqrt{2n}\pi(1-\pi)} \right)$$
* **Interpretation**: A $P\text{-value} \ge 0.01$ passes. 
  - A low run count indicates too few transitions (bits "clumping" together).
  - A high run count indicates too many transitions (the stream oscillates too rapidly like `010101`).

### 4. Chi-Square ($\chi^2$) Goodness-of-Fit Tests
These tests check whether the frequencies of observed blocks of bits match the theoretical uniform distribution.
* **Formula**:
  $$\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}$$
  where:
  - $O_i$ is the observed frequency count of category $i$.
  - $E_i$ is the expected frequency count of category $i$ under a uniform distribution.
  - $k$ is the number of categories.
* **Implemented Tests**:
  - **Bit-Pair (2-bit) Test**: Groups bits into non-overlapping pairs (`00`, `01`, `10`, `11`). The categories $k = 4$, and the expected count is $E_i = N_{\text{pairs}}/4$. (Degrees of freedom $df = k - 1 = 3$).
  - **Byte-Level (8-bit) Test**: Groups bits into bytes (numerical values $0$ to $255$). The categories $k = 256$, and the expected count is $E_i = N_{\text{bytes}}/256$. (Degrees of freedom $df = 255$).
* **P-value Calculation**: The p-value is computed using the Chi-Square survival function (cumulative upper-tail probability):
  $$P\text{-value} = Q(\chi^2, df) = 1 - F(\chi^2, df)$$
  A $P\text{-value} \ge 0.01$ indicates that the observed distribution is statistically uniform.

### 5. Serial Correlation (Lag 1)
Measures the linear association between adjacent bits to see if the value of a bit depends on the preceding bit.
* **Formula**:
  $$r_1 = \frac{\sum_{i=1}^{n-1} (X_i - \mu)(X_{i+1} - \mu)}{\sum_{i=1}^n (X_i - \mu)^2}$$
  where $\mu$ is the mean value of all bits.
* **Interpretation**: A truly random sequence has $r_1$ close to `0.0`. Positive values indicate that identical bits tend to follow each other, while negative values suggest alternating bits.

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

