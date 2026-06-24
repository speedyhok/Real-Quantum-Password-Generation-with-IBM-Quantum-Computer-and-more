import math
import numpy as np
import scipy.stats as stats

def shannon_entropy(bitstring):
    """
    Calculates the Shannon entropy of a binary string.
    Ideal value is 1.0 (fully random).
    """
    n = len(bitstring)
    if n == 0:
        return 0.0
    
    n0 = bitstring.count('0')
    n1 = bitstring.count('1')
    
    p0 = n0 / n
    p1 = n1 / n
    
    entropy = 0.0
    if p0 > 0:
        entropy -= p0 * math.log2(p0)
    if p1 > 0:
        entropy -= p1 * math.log2(p1)
    
    return entropy

def nist_monobit_test(bitstring):
    """
    NIST SP 800-22 Frequency (Monobit) Test.
    Tests if the proportion of 0s and 1s is approximately 0.5.
    Returns: (statistic, p_value, pass_boolean)
    A p-value >= 0.01 indicates the sequence is random.
    """
    n = len(bitstring)
    if n == 0:
        return 0.0, 0.0, False
    
    # Convert bits to -1 and +1
    s = [1 if b == '1' else -1 for b in bitstring]
    s_sum = sum(s)
    
    s_obs = abs(s_sum) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2))
    
    return s_sum, p_value, p_value >= 0.01

def nist_runs_test(bitstring):
    """
    NIST SP 800-22 Runs Test.
    Tests if the number of runs (consecutive identical bits) is as expected.
    Returns: (observed_runs, p_value, pass_boolean)
    A p-value >= 0.01 indicates the sequence is random.
    """
    n = len(bitstring)
    if n < 2:
        return 0, 0.0, False
    
    # Step 1: Pre-test proportion of ones
    n1 = bitstring.count('1')
    pi = n1 / n
    
    # If the proportion of ones is too far from 0.5, the runs test is not valid / fails
    tau = 2 / math.sqrt(n)
    if abs(pi - 0.5) >= tau:
        # According to NIST, if this condition is met, the test fails (p-value = 0.0)
        return 0, 0.0, False
    
    # Step 2: Count the observed number of runs
    # A run is a sequence of consecutive identical bits.
    # We count transitions and add 1.
    v_obs = 1
    for i in range(n - 1):
        if bitstring[i] != bitstring[i + 1]:
            v_obs += 1
            
    # Step 3: Compute p-value
    numerator = abs(v_obs - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    
    try:
        p_value = math.erfc(numerator / denominator)
    except ZeroDivisionError:
        p_value = 0.0
        
    return v_obs, p_value, p_value >= 0.01

def chisquare_bit_pair_test(bitstring):
    """
    Chi-Square uniformity test on 2-bit pairs (00, 01, 10, 11).
    Degrees of freedom = 3.
    """
    n = len(bitstring)
    num_pairs = n // 2
    if num_pairs < 4:
        return 0.0, 1.0, True  # Not enough data
    
    # Create non-overlapping pairs
    pairs = [bitstring[i:i+2] for i in range(0, num_pairs * 2, 2)]
    
    categories = ['00', '01', '10', '11']
    observed = [pairs.count(cat) for cat in categories]
    expected = [num_pairs / 4] * 4
    
    # Compute Chi-Square statistic
    chi2_stat = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
    p_value = stats.chi2.sf(chi2_stat, 3)
    
    return float(chi2_stat), float(p_value), bool(p_value >= 0.01)

def chisquare_byte_test(bitstring):
    """
    Chi-Square uniformity test at the byte (8-bit) level.
    Splits the bitstring into bytes (values 0-255).
    Degrees of freedom = 255.
    """
    n = len(bitstring)
    num_bytes = n // 8
    
    if num_bytes < 10:
        # Not enough bytes for a meaningful byte-level chi-square test
        return 0.0, 1.0, True
    
    # Convert chunks of 8 bits into byte values (0-255)
    bytes_list = []
    for i in range(0, num_bytes * 8, 8):
        byte_val = int(bitstring[i:i+8], 2)
        bytes_list.append(byte_val)
        
    # Count frequencies of each byte value
    observed = np.zeros(256)
    for b in bytes_list:
        observed[b] += 1
        
    expected_freq = num_bytes / 256.0
    
    # Chi-square formula: sum((O - E)^2 / E)
    chi2_stat = np.sum((observed - expected_freq) ** 2 / expected_freq)
    
    # Survival function for chi-square with 255 DoF
    p_value = stats.chi2.sf(chi2_stat, 255)
    
    return float(chi2_stat), float(p_value), bool(p_value >= 0.01)

def serial_correlation(bitstring):
    """
    Calculates the serial correlation coefficient (autocorrelation at lag 1).
    Shows if the next bit depends on the current bit.
    Ideal value is 0.0 (no correlation).
    """
    n = len(bitstring)
    if n < 2:
        return 0.0
    
    # Convert bits to numeric values
    x = np.array([int(b) for b in bitstring])
    x_mean = np.mean(x)
    
    numerator = np.sum((x[:-1] - x_mean) * (x[1:] - x_mean))
    denominator = np.sum((x - x_mean) ** 2)
    
    if denominator == 0:
        return 0.0
        
    return float(numerator / denominator)

def run_all_tests(bitstring):
    """
    Runs all implemented randomness tests on a bitstring and returns the results.
    """
    entropy = shannon_entropy(bitstring)
    mono_stat, mono_p, mono_pass = nist_monobit_test(bitstring)
    runs_obs, runs_p, runs_pass = nist_runs_test(bitstring)
    pair_stat, pair_p, pair_pass = chisquare_bit_pair_test(bitstring)
    byte_stat, byte_p, byte_pass = chisquare_byte_test(bitstring)
    correlation = serial_correlation(bitstring)
    
    return {
        "length": len(bitstring),
        "entropy": entropy,
        "nist_monobit": {
            "stat": mono_stat,
            "p_value": mono_p,
            "passed": mono_pass
        },
        "nist_runs": {
            "observed_runs": runs_obs,
            "p_value": runs_p,
            "passed": runs_pass
        },
        "chi_square_pair": {
            "stat": pair_stat,
            "p_value": pair_p,
            "passed": pair_pass
        },
        "chi_square_byte": {
            "stat": byte_stat,
            "p_value": byte_p,
            "passed": byte_pass
        },
        "serial_correlation": correlation
    }
