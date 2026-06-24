# Quantum Random Password Generator with Randomness Quality Analysis

**Author:** Mohibul Hoque ([Hokworks@gmail.com](mailto:Hokworks@gmail.com) | [LinkedIn](https://www.linkedin.com/in/speedymohibul))  
**Date:** June 2026  
**Language/Libraries:** Python 3, Qiskit 2.4.2, Qiskit Aer 0.17.2, Streamlit, SciPy, NumPy, zxcvbn

---

## 1. Introduction & Executive Summary

In cryptographic applications, the quality of a random key or password directly determines its security. If an attacker can predict the output of a random number generator, the encryption or credentials can be compromised, regardless of the key length. 

Traditional computers rely on **Pseudorandom Number Generators (PRNGs)** (e.g., the Mersenne Twister used in Python's standard `random` module). PRNGs use deterministic mathematical formulas starting from a initial state called a *seed*. If the seed is known or guessed, the entire sequence is predictable. **Cryptographically Secure Pseudorandom Number Generators (CSPRNGs)** (e.g., Python's `secrets` module) leverage operating system entropy (such as mouse movements, disk seek times, and network activity) to generate less predictable keys, but these remain fundamentally classical and deterministic at their core.

This project implements a **Quantum Random Number Generator (QRNG)** using Qiskit. By leveraging the intrinsic non-deterministic behavior of quantum superposition and measurement, we tap into a source of true physical randomness. We build a Streamlit web application that:
1. Generates passwords using quantum bits.
2. Compares physical quantum hardware (IBM Quantum) against local simulation (Qiskit Aer).
3. Evaluates the randomness quality of the quantum streams against classical PRNGs and CSPRNGs using statistical tests (Shannon Entropy, NIST Monobit, NIST Runs, Chi-Square tests).
4. Evaluates generated password strength using the `zxcvbn` library.
5. Discusses the impact of quantum noise (gate errors, decoherence, and readout errors) on real superconducting hardware.

---

## 2. Quantum Physics Foundations

According to quantum mechanics, certain physical processes are fundamentally random. We model this behavior in a quantum circuit:

### 2.1 Qubit Superposition
A classical bit can only exist in state $0$ or $1$. A quantum bit (qubit) can exist in a linear combination of both states, known as a superposition:
$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$
where $\alpha, \beta \in \mathbb{C}$ are probability amplitudes, satisfying the normalization condition:
$$|\alpha|^2 + |\beta|^2 = 1$$

To generate random bits, we initialize qubits in the ground state $|0\rangle$ and apply a **Hadamard ($H$) gate**. The Hadamard gate performs a rotation on the Bloch sphere, transforming the basis states as follows:
$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$$

For a system of $N$ qubits, applying a Hadamard gate to each qubit yields an equal superposition of all $2^N$ possible states:
$$|\Psi\rangle = H^{\otimes N} |0\rangle^{\otimes N} = \frac{1}{\sqrt{2^N}} \sum_{x=0}^{2^N-1} |x\rangle$$

### 2.2 Wave Function Collapse (The Born Rule)
When we measure the qubits in the computational ($Z$) basis, the superposition collapses into one of the basis states. According to the **Born Rule**, the probability $P(x)$ of measuring state $|x\rangle$ is:
$$P(x) = |\langle x | \Psi \rangle|^2 = \left| \frac{1}{\sqrt{2^N}} \right|^2 = \frac{1}{2^N}$$

For a single qubit, the probability of measuring $0$ is exactly $0.5$, and the probability of measuring $1$ is exactly $0.5$. This collapse is a fundamental, non-deterministic physical process. It does not rely on hidden variables, making it a source of true, physical randomness.

---

## 3. Modulo Bias Mitigation: Rejection Sampling

When converting a random bitstream into a password, we map raw bits to a character set (alphabet) of size $A$ (e.g., $A=72$ for alphanumeric characters and symbols). 

### 3.1 The Problem with Modulo Arithmetic
A common but flawed approach to map a random integer $X \in [0, M-1]$ to a range $[0, A-1]$ is:
$$\text{index} = X \bmod A$$
If $M$ (which is $2^k$ for a $k$-bit number) is not a perfect multiple of $A$, this introduces **modulo bias**. The first $M \bmod A$ characters of the alphabet will have a higher probability of being chosen than the remaining characters. 

*Example:* If we use $k=3$ bits ($M=8$ possible values: $0$ to $7$) to select from an alphabet of size $A=3$ (characters $a, b, c$):
- $0, 3, 6 \bmod 3 \implies 0$ (character $a$) — Probability: $3/8 = 0.375$
- $1, 4, 7 \bmod 3 \implies 1$ (character $b$) — Probability: $3/8 = 0.375$
- $2, 5 \bmod 3 \implies 2$ (character $c$) — Probability: $2/8 = 0.250$

This bias degrades the statistical entropy of the passwords, making them easier to crack.

### 3.2 Mitigation via Rejection Sampling
To achieve absolute uniformity, we implement **Rejection Sampling**:
1. Determine the minimum number of bits $k$ required per character: $k = \lceil \log_2(A) \rceil$, which guarantees $2^k \ge A$.
2. Compute the largest multiple of $A$ that is less than or equal to $2^k$:
   $$\text{limit} = 2^k - (2^k \bmod A)$$
3. Read $k$ bits from the quantum random stream to form an integer $X \in [0, 2^k - 1]$.
4. If $X < \text{limit}$, we accept the character index:
   $$\text{index} = X \bmod A$$
5. If $X \ge \text{limit}$, we reject $X$ (discarding the $k$ bits) and read the next $k$ bits from the stream.

Since we only accept values in the range $[0, \text{limit}-1]$, and this range is a perfect multiple of $A$, every character in our alphabet has an exactly equal probability of being selected:
$$P(\text{index} = i) = \frac{1}{A}$$
This ensures the quantum randomness is preserved in the final password.

---

## 4. Randomness Quality Analysis Methodology

To evaluate the randomness of our bitstreams, we implement a suite of statistical tests:

### 4.1 Shannon Entropy
Shannon entropy measures the uncertainty or information density in a sequence. For a binary string, it is calculated as:
$$H = -\sum_{i \in \{0, 1\}} p_i \log_2(p_i)$$
where $p_i$ is the observed frequency of bit value $i$. The ideal value for a truly random binary sequence is **$1.0$ bits per bit**.

### 4.2 NIST Monobit Frequency Test (SP 800-22 Test 1)
Tests if the proportion of zeros and ones in a sequence is approximately equal.
- Convert bits $X_i \in \{0, 1\}$ to $S_i \in \{-1, +1\}$.
- Compute the sum $S_n = \sum_{i=1}^n S_i$.
- Calculate the test statistic: $S_{obs} = \frac{|S_n|}{\sqrt{n}}$.
- Compute the p-value:
  $$P\text{-value} = \text{erfc}\left( \frac{S_{obs}}{\sqrt{2}} \right)$$
- If $P\text{-value} \ge 0.01$, the sequence is considered random.

### 4.3 NIST Runs Test (SP 800-22 Test 3)
Tests if the frequency of transitions between consecutive zeros and ones is as expected. A "run" is an uninterrupted sequence of identical bits.
- Let $\pi = \frac{1}{n} \sum X_i$ be the proportion of ones.
- Compute the observed number of runs:
  $$V_n = 1 + \sum_{j=1}^{n-1} (X_j \oplus X_{j+1})$$
- Compute the p-value:
  $$P\text{-value} = \text{erfc}\left( \frac{|V_n - 2n\pi(1-\pi)|}{2\sqrt{2n}\pi(1-\pi)} \right)$$
- If $P\text{-value} \ge 0.01$, the sequence passes.

### 4.4 Chi-Square ($\chi^2$) Uniformity Tests
We run two goodness-of-fit uniformity tests:
1. **Bit-Pair Test (2-bit):** Splits the stream into non-overlapping pairs (00, 01, 10, 11). Expected count for each pair is $N_{\text{pairs}}/4$. (Degrees of freedom = 3).
2. **Byte-Level Test (8-bit):** Groups bits into bytes (values 0-255). Expected frequency is $N_{\text{bytes}}/256$. (Degrees of freedom = 255).

The Chi-Square statistic is calculated as:
$$\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$$
where $O_i$ is the observed count and $E_i$ is the expected count. We calculate the p-value using the Chi-Square survival function. A $P\text{-value} \ge 0.01$ indicates uniformity.

### 4.5 Serial Correlation (Lag 1)
Measures the correlation between adjacent bits ($X_i$ and $X_{i+1}$).
$$r_1 = \frac{\sum_{i=1}^{n-1} (X_i - \mu)(X_{i+1} - \mu)}{\sum_{i=1}^n (X_i - \mu)^2}$$
where $\mu$ is the mean of the sequence. For a truly random sequence, $r_1$ should be close to **$0.0$** (no linear correlation).

---

## 5. Quantum Noise & Real Hardware Analysis

When comparing the **Local Qiskit Aer Simulator** and the **IBM Quantum Real Hardware**, we observe statistical differences due to physical quantum noise:

| Source of Difference | Qiskit Aer Simulator | IBM Quantum Hardware |
| :--- | :--- | :--- |
| **System Type** | Closed, idealized mathematical model | Open physical superconducting qubits |
| **Gate Fidelity** | Perfect ($100\%$ accuracy) | Imperfect ($99.0\% - 99.9\%$ fidelity) |
| **Decoherence** | Infinite lifetime | Finite relaxation ($T_1$) and dephasing ($T_2$) times |
| **Readout Error** | None ($100\%$ measurement accuracy) | Imperfect readout ($1\% - 5\%$ error rates) |
| **NIST P-values** | Consistently high ($0.1 - 0.9$) | Highly variable; can occasionally fail due to bias |

### 5.1 Noise Manifestation in Randomness Tests
1. **Decoherence ($T_1$ Decay):** Over time, qubits in superposition release energy to the environment and decay to the $|0\rangle$ state. If a job waits in a queue or if gate execution is slow, qubits decay, causing the bitstream to have an excess of `0`s (biasing the monobit test).
2. **Readout Errors:** Superconducting qubits are measured by measuring microwave transmission through coupled resonators. Thermal fluctuations can cause a $|1\rangle$ state to register as a $|0\rangle$, creating systemic read biases.
3. **Crosstalk & Autocorrelation:** Superconducting qubits laid out on a 2D grid experience capacitive coupling. Measuring qubit $A$ can disturb qubit $B$, introducing correlations (which degrades runs and serial correlation tests).

### 5.2 Real-World Security Mitigations
In professional security applications, raw physical entropy is never used directly. It is passed through a **randomness extractor** (e.g., the Von Neumann debiasing algorithm, or cryptographic hash functions like SHA-256) to concentrate the entropy and eliminate physical hardware bias, converting the raw physical bits into a uniform distribution.

---

## 6. How to Run the Project

### 6.1 Prerequisites
Make sure Python 3.10+ is installed. Clone the repository and navigate to the project directory:
```bash
cd "C:\Users\Administrator\Desktop\Quantum Password"
```

### 6.2 Installation
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 6.3 Launching the Web Interface
Run the Streamlit application:
```bash
streamlit run app.py
```
Open the local URL displayed in the terminal (typically `http://localhost:8501`).

---

## 7. Conclusions

This project successfully demonstrates the implementation and analysis of a **Quantum Random Password Generator**. While classical PRNGs are sufficient for general applications, they are deterministic. Quantum systems offer a source of true, non-deterministic randomness grounded in the laws of physics. 

However, our rigorous analysis highlights a key lesson of the NISQ era: **real quantum hardware is noisy**. While simulated quantum circuits produce mathematically perfect randomness, physical superconducting qubits exhibit slight biases and correlations due to thermal decay, gate inaccuracies, and readout errors. This proves that for cryptographic deployment, physical quantum entropy must be paired with classical randomness extraction post-processing.
